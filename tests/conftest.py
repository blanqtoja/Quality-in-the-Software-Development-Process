"""
Shared Pytest fixtures (conftest.py) for the entire testing team.

Provides:
- automatic detection of a running ERP backend (Docker/Spring Boot on :8081 or :8080)
  with seamless fallback to the built-in contract-faithful ErpReferenceTransport,
- pre-configured HTTP clients for each RBAC role (admin_client, accountant_client,
  warehouse_client, sales_client, guest_client, unauth_client),
- TestDataFactory fixture (data_factory) and master-data setup fixtures (seeded_item, seeded_partner).
"""

from __future__ import annotations

import os
from typing import Iterator

import httpx
import pytest

from tests.assertions import assert_valid_model
from tests.client import ErpApiClient
from tests.config import ApiSettings, ErpRole
from tests.factories import TestDataFactory
from tests.local_erp_server import ErpReferenceTransport
from tests.models import ItemResponseModel, PartnerResponseModel


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
def base_api_client() -> Iterator[ErpApiClient]:
    """
    Session-scoped base HTTP client sharing the JWT token cache across tests.
    Connects over TCP if a live Spring Boot container is reachable (via ERP_BASE_URL,
    localhost:8081, or localhost:8080); otherwise uses the contract-faithful
    in-memory ErpReferenceTransport so tests execute reliably out of the box.
    """
    env_url = os.getenv("ERP_BASE_URL")
    candidate_urls = [env_url.rstrip("/")] if env_url else ["http://localhost:8081", "http://localhost:8080"]

    live_url: str | None = None
    for url in candidate_urls:
        if url and _probe_server(url):
            live_url = url
            break

    if live_url is not None:
        settings = ApiSettings(base_url=live_url)
        client = ErpApiClient(settings=settings, transport=None)
    else:
        settings = ApiSettings(base_url="http://localhost:8081")
        client = ErpApiClient(settings=settings, transport=ErpReferenceTransport())

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
