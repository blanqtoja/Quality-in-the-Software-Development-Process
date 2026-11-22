"""
Shared Pytest fixtures (conftest.py) for the entire testing team (API + Frontend E2E).

Provides:
- automatic detection of a running ERP backend (Spring Boot on :8080 or :8081)
  with seamless fallback to the built-in contract-faithful ErpReferenceTransport,
- pre-configured HTTP clients for each RBAC role (admin_client, accountant_client,
  warehouse_client, sales_client, guest_client, unauth_client),
- TestDataFactory fixture (data_factory) and master-data setup fixtures (seeded_item, seeded_partner),
- automatic SPA + Reverse-Proxy server (ErpFrontendSpaServer) serving the built React 19
  frontend (`ERPSystem/frontend/dist`) connected to the active backend,
- isolated Playwright browser contexts (`ui_page`) and ready-to-use Page Objects
  (`login_page`, `dashboard_page`, `audit_page`, `master_data_page`, `ledger_page`, `sales_page`).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import httpx
import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from tests.assertions import assert_valid_model
from tests.client import ErpApiClient
from tests.config import ApiSettings, ErpRole
from tests.factories import TestDataFactory
from tests.local_erp_server import ErpReferenceTransport
from tests.models import ItemResponseModel, PartnerResponseModel
from tests.pages import (
    AuditPage,
    DashboardPage,
    LedgerPage,
    LoginPage,
    MasterDataPage,
    SalesPage,
    PurchasingPage,
    ReportingPage,
)
from tests.ui import ErpFrontendSpaServer


def _probe_server(url: str) -> bool:
    """Checks whether an external Spring Boot ERP server is reachable at the given URL."""
    try:
        resp = httpx.post(
            f"{url}/api/auth/login",
            json={"username": "guest", "password": "guest"},
            timeout=1.5,
        )
        return resp.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def base_api_client(request: pytest.FixtureRequest) -> Iterator[ErpApiClient]:
    """
    Session-scoped base HTTP client sharing the JWT token cache across tests.
    Connects over TCP if a live Spring Boot server is reachable (via ERP_BASE_URL,
    localhost:8080, or localhost:8081); otherwise uses the contract-faithful
    in-memory ErpReferenceTransport so tests execute reliably out of the box.
    """
    env_url = os.getenv("ERP_BASE_URL")
    backend_mode = os.getenv("ERP_BACKEND_MODE", "auto")
    if backend_mode not in {"auto", "live", "reference"}:
        pytest.fail(f"Invalid ERP_BACKEND_MODE: {backend_mode}", pytrace=False)
    candidate_urls = (
        [env_url.rstrip("/")]
        if env_url
        else ["http://localhost:8080", "http://localhost:8081"]
    )

    live_url: str | None = None
    for url in ([] if backend_mode == "reference" else candidate_urls):
        if url and _probe_server(url):
            live_url = url
            break

    if live_url is None and backend_mode == "live":
        pytest.fail(f"Live ERP unavailable at {candidate_urls}; no reference fallback in live mode.", pytrace=False)
    if live_url is not None:
        settings = ApiSettings(base_url=live_url)
        client = ErpApiClient(settings=settings, transport=None)
    else:
        settings = ApiSettings(base_url="http://localhost:8080")
        client = ErpApiClient(settings=settings, transport=ErpReferenceTransport())

    metadata = getattr(request.config, "_erp_report_metadata", {})
    metadata["ERP backend"] = live_url or "REFERENCE: in-memory test double, not Spring Boot"

    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def admin_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """API client authenticated with the ADMIN role."""
    client = base_api_client.with_role(ErpRole.ADMIN)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def accountant_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """API client authenticated with the ACCOUNTANT role."""
    client = base_api_client.with_role(ErpRole.ACCOUNTANT)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def warehouse_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """API client authenticated with the WAREHOUSE role."""
    client = base_api_client.with_role(ErpRole.WAREHOUSE)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def sales_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """API client authenticated with the SALES role."""
    client = base_api_client.with_role(ErpRole.SALES)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def guest_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """API client authenticated with the read-only GUEST account."""
    client = base_api_client.with_role(ErpRole.GUEST)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def unauth_client(base_api_client: ErpApiClient) -> Iterator[ErpApiClient]:
    """Unauthenticated API client (for testing 401 Unauthorized responses)."""
    client = base_api_client.with_role(None)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def data_factory() -> type[TestDataFactory]:
    """Provides the TestDataFactory helper class."""
    return TestDataFactory


@pytest.fixture
def seeded_item(admin_client: ErpApiClient, data_factory: type[TestDataFactory]) -> ItemResponseModel:
    """Fixture that creates a unique item in MasterData prior to test execution."""
    payload = data_factory.item_payload()
    response = admin_client.post("/api/masterdata/items", json=payload)
    return assert_valid_model(response, ItemResponseModel, expected_status=201)


@pytest.fixture
def seeded_partner(admin_client: ErpApiClient, data_factory: type[TestDataFactory]) -> PartnerResponseModel:
    """Fixture that creates a unique business partner (vendor & customer) prior to test execution."""
    payload = data_factory.partner_payload()
    response = admin_client.post("/api/masterdata/partners", json=payload)
    return assert_valid_model(response, PartnerResponseModel, expected_status=201)


# ==============================================================================
# Frontend E2E Fixtures (Playwright + Page Object Model)
# ==============================================================================


@pytest.fixture(scope="session")
def frontend_base_url(base_api_client: ErpApiClient, request: pytest.FixtureRequest) -> Iterator[str]:
    """
    Provides the base URL for the ERP React 19 Single-Page Application.
    If ERP_FRONTEND_URL is set, uses that URL directly; otherwise starts an embedded
    ErpFrontendSpaServer serving `ERPSystem/frontend/dist` and reverse-proxying `/api/*`
    to the active backend (live Spring Boot server or reference transport).
    """
    explicit_frontend_url = os.getenv("ERP_FRONTEND_URL")
    if explicit_frontend_url:
        if base_api_client._transport is not None:
            pytest.fail("An explicit frontend requires its real ERP_BASE_URL; API fixtures must not use a separate reference backend.", pytrace=False)
        getattr(request.config, "_erp_report_metadata", {})["ERP frontend"] = explicit_frontend_url
        yield explicit_frontend_url.rstrip("/")
        return

    dist_dir = Path(os.environ["ERP_FRONTEND_DIST"]) if os.getenv("ERP_FRONTEND_DIST") else None
    options = {"dist_dir": dist_dir} if dist_dir is not None else {}
    spa_server = ErpFrontendSpaServer(
        backend_base_url=base_api_client.settings.base_url,
        backend_transport=base_api_client._transport,
        **options,
    )
    if not (spa_server.dist_dir / "index.html").is_file():
        pytest.fail(f"Frontend build missing at {spa_server.dist_dir}. Set ERP_FRONTEND_URL or ERP_FRONTEND_DIST.", pytrace=False)
    url = spa_server.start()
    getattr(request.config, "_erp_report_metadata", {})["ERP frontend"] = f"{url} (React build: {spa_server.dist_dir})"
    try:
        yield url
    finally:
        spa_server.stop()


@pytest.fixture(scope="session")
def playwright_browser() -> Iterator[Browser]:
    """
    Launches a headless Chromium-based browser for Frontend E2E tests.
    Automatically uses installed Microsoft Edge ('msedge'), Chrome ('chrome'),
    or bundled Playwright Chromium.
    """
    headless = os.getenv("ERP_HEADED", "0") not in ("1", "true", "TRUE")
    pw = sync_playwright().start()
    browser: Browser | None = None
    last_err: Exception | None = None

    selected_channel = os.getenv("ERP_BROWSER_CHANNEL")
    channels = ([None] if selected_channel == "chromium" else [selected_channel]) if selected_channel else ("msedge", "chrome", None)
    for channel in channels:
        try:
            if channel:
                browser = pw.chromium.launch(channel=channel, headless=headless)
            else:
                browser = pw.chromium.launch(headless=headless)
            break
        except Exception as exc:
            last_err = exc

    if browser is None:
        pw.stop()
        raise RuntimeError(f"Could not launch Chromium/Edge browser via Playwright: {last_err}")

    try:
        yield browser
    finally:
        browser.close()
        pw.stop()


@pytest.fixture
def ui_page(playwright_browser: Browser, frontend_base_url: str) -> Iterator[Page]:
    """
    Provides a clean, isolated Playwright browser Page per test with English locale,
    desktop viewport (1440x900), and onboarding spotlight tour disabled.
    """
    context = playwright_browser.new_context(
        viewport={"width": 1440, "height": 900},
        locale="en-US",
        base_url=frontend_base_url,
    )
    page = context.new_page()
    page.add_init_script(
        """
        window.localStorage.setItem('erp.locale', 'en');
        window.localStorage.setItem(
            'erp.onboarding',
            JSON.stringify({ completed: true, currentStep: 99 })
        );
        """
    )
    try:
        yield page
    finally:
        context.close()


@pytest.fixture
def login_page(ui_page: Page, frontend_base_url: str) -> LoginPage:
    """Page Object fixture for `/login`."""
    return LoginPage(ui_page, frontend_base_url)


@pytest.fixture
def dashboard_page(ui_page: Page, frontend_base_url: str) -> DashboardPage:
    """Page Object fixture for `/` (Dashboard & Reconciliation Hero)."""
    return DashboardPage(ui_page, frontend_base_url)


@pytest.fixture
def audit_page(ui_page: Page, frontend_base_url: str) -> AuditPage:
    """Page Object fixture for `/audit` and RBAC 403 Forbidden screen."""
    return AuditPage(ui_page, frontend_base_url)


@pytest.fixture
def master_data_page(ui_page: Page, frontend_base_url: str) -> MasterDataPage:
    """Page Object fixture for `/masterdata` (Items, Partners, Warehouses, Locations)."""
    return MasterDataPage(ui_page, frontend_base_url)


@pytest.fixture
def ledger_page(ui_page: Page, frontend_base_url: str) -> LedgerPage:
    """Page Object fixture for `/ledger` (Manual Journal Entries, Reversal, Periods)."""
    return LedgerPage(ui_page, frontend_base_url)


@pytest.fixture
def sales_page(ui_page: Page, frontend_base_url: str) -> SalesPage:
    """Page Object fixture for `/sales` (Sales Orders, Deliveries, Invoices)."""
    return SalesPage(ui_page, frontend_base_url)


@pytest.fixture
def purchasing_page(ui_page: Page, frontend_base_url: str) -> PurchasingPage:
    return PurchasingPage(ui_page, frontend_base_url)


@pytest.fixture
def reporting_page(ui_page: Page, frontend_base_url: str) -> ReportingPage:
    return ReportingPage(ui_page, frontend_base_url)


@pytest.hookimpl(optionalhook=True)
def pytest_metadata(metadata: dict, config: pytest.Config) -> None:
    config._erp_report_metadata = metadata
    metadata["ERP backend mode"] = os.getenv("ERP_BACKEND_MODE", "auto")
    metadata["ERP backend"] = "not initialized (collection or setup incomplete)"
