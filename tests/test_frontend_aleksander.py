"""
Frontend E2E Test Suite — Owner: Aleksander Kazmierczak (Student ID: 251544)

Implements 4 structured Frontend E2E test cases using Playwright and the Page Object Model (POM),
testing the exact same domain invariants and operations through the React 19 + Mantine v9 UI
as the REST API test suite:
- 2x Happy Path tests (TC-UI-AK-01, TC-UI-AK-03)
- 2x Negative / Guard Path tests (TC-UI-AK-02, TC-UI-AK-04)

Architecture adheres strictly to DRY and Single Responsibility Principles:
all DOM locators and Mantine component interactions are encapsulated in `tests/pages/`.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.assertions import assert_decimal_equal, assert_valid_model
from tests.client import ErpApiClient
from tests.config import ErpRole
from tests.factories import TestDataFactory
from tests.models import PartnerResponseModel, TrialBalanceReportModel
from tests.pages import (
    AuditPage,
    DashboardPage,
    LedgerPage,
    LoginPage,
    MasterDataPage,
)


@pytest.mark.aleksander
@pytest.mark.frontend
class TestFrontendAleksander:
    """Frontend E2E tests verifying the React SPA against the live ERP backend (4 test cases)."""

    @pytest.mark.happy_path
    def test_tc_ui_ak_01_reconciliation_hero_happy_path(
        self,
        login_page: LoginPage,
        dashboard_page: DashboardPage,
    ) -> None:
        """
        ID: TC-UI-AK-01 (Mirrors API Test: TC-API-AK-01 — GET /api/reporting/reconciliation)
        Owner: Aleksander Kazmierczak (251544)
        Priority: P0 (Critical)
        View / Component: Dashboard (`/`) -> ReconciliationHero (`[data-onboarding="reconciliation-hero"]`)
        Preconditions:
            - ERP backend and React SPA frontend are running.
            - User authenticates via the `/login` form with role ACCOUNTANT (`accountant`).
            - General Ledger and subledgers (AR, AP, Inventory) are in a consistent state.
        Postconditions:
            - Dashboard renders the 'Books reconcile' heading and 'Trial balance balanced' badge.
            - Every subledger row (1200, 2100, 1310...) displays a green 'Reconciled' status icon.
            - Every transitional clearing account card displays a green 'Cleared' status icon.
        """
        # Step 1: Open /login and sign in as ACCOUNTANT via the UI form
        login_page.login_as_role(ErpRole.ACCOUNTANT)

        # Step 2: Verify Dashboard header displays the signed-in accountant identity and role badge
        dashboard_page.expect_signed_in_identity("accountant", expected_role_badge="ACCOUNTANT")

        # Step 3: Verify the Reconciliation Hero card confirms 'Books reconcile' & 'Trial balance balanced'
        dashboard_page.expect_reconciliation_healthy()

        # Step 4: Verify all subledger control rows (AR, AP, Inventory) show 'Reconciled'
        reconciled_count = dashboard_page.expect_all_subledgers_reconciled()
        assert reconciled_count >= 3

        # Step 5: Verify all transitional clearing accounts (GR/IR, WIP) show 'Cleared'
        cleared_count = dashboard_page.expect_all_clearing_accounts_cleared()
        assert cleared_count >= 2

    @pytest.mark.negative_path
    def test_tc_ui_ak_02_guest_audit_trail_rbac_403_forbidden(
        self,
        login_page: LoginPage,
        dashboard_page: DashboardPage,
        audit_page: AuditPage,
    ) -> None:
        """
        ID: TC-UI-AK-02 (Mirrors API Test: TC-API-AK-04 — GET /api/audit 403 Forbidden RBAC)
        Owner: Aleksander Kazmierczak (251544)
        Priority: P1 (High)
        View / Component: Sidebar Navigation & `/audit` -> `ForbiddenPage` (`<RequireRole role="ADMIN">`)
        Preconditions:
            - ERP backend and React SPA frontend are running with RBAC active.
            - User enters the application via 'Browse as guest (read-only)' (`GUEST` role).
        Postconditions:
            - The 'Audit Trail' link is hidden in the AppShell sidebar navigation for GUEST.
            - Direct navigation to `/audit` is intercepted by `<RequireRole role="ADMIN">`,
              rendering the 403 Forbidden page without leaking audit log records.
            - Clicking 'Back to dashboard' returns the user safely to `/`.
        """
        # Step 1: Open /login and click 'Browse as guest (read-only)'
        login_page.open()
        login_page.login_as_guest()

        # Step 2: Verify GUEST identity on Dashboard and confirm 'Audit Trail' is hidden in sidebar
        dashboard_page.expect_signed_in_identity("guest")
        dashboard_page.expect_sidebar_link_hidden("Audit Trail")

        # Step 3: Attempt direct URL navigation to the restricted /audit route
        audit_page.open_directly()

        # Step 4: Verify the 403 Forbidden guard screen is rendered
        audit_page.expect_forbidden_403_view()

        # Step 5: Click 'Back to dashboard' and verify navigation back to '/'
        audit_page.click_back_to_dashboard()

    @pytest.mark.happy_path
    def test_tc_ui_ak_03_create_business_partner_modal_happy_path(
        self,
        login_page: LoginPage,
        master_data_page: MasterDataPage,
        admin_client: ErpApiClient,
        data_factory: type[TestDataFactory],
    ) -> None:
        """
        ID: TC-UI-AK-03 (Mirrors API Test: TC-API-AK-05 — POST /api/masterdata/partners)
        Owner: Aleksander Kazmierczak (251544)
        Priority: P1 (High)
        View / Component: `/masterdata` -> `PartnersPanel` -> 'New partner' Modal & DataTable
        Preconditions:
            - ERP backend and React SPA frontend are running.
            - User is authenticated in the UI as ADMIN (`admin`).
            - Unique partner code (`PRT-...`) generated via TestDataFactory.
        Postconditions:
            - Submitting the 'New partner' modal displays toast 'Partner <CODE> created'.
            - Modal closes and the new partner row is visible in the UI DataTable with
              both 'Vendor' and 'Customer' badges and 45-day payment terms.
            - Backend API confirms the partner is persisted in PostgreSQL.
        """
        payload = data_factory.partner_payload(
            name="Precision Robotics Partner UI SA",
            vendor=True,
            customer=True,
            payment_terms_days=45,
        )
        partner_code = payload["code"]
        partner_name = payload["name"]

        # Step 1: Log in as ADMIN via the UI
        login_page.login_as_role(ErpRole.ADMIN)

        # Step 2: Navigate to Master Data via the left sidebar
        master_data_page.navigate_via_sidebar("Master Data")
        master_data_page.expect_pathname("/masterdata")

        # Step 3: Open the 'Partners' tab, launch 'New partner' modal, fill fields, and submit
        master_data_page.create_partner_via_modal(
            code=partner_code,
            name=partner_name,
            vendor=True,
            customer=True,
            tax_id=payload["taxId"],
            payment_terms_days=45,
            ap_account_code="2100",
            ar_account_code="1200",
        )

        # Step 4: Verify the newly created partner appears in the UI DataTable with expected badges
        master_data_page.expect_partner_in_table(
            code=partner_code,
            name=partner_name,
            vendor=True,
            customer=True,
            payment_terms_days=45,
        )

        # Step 5: Cross-verify backend persistence via GET /api/masterdata/partners
        api_resp = admin_client.get("/api/masterdata/partners")
        assert api_resp.status_code == 200
        partners = [PartnerResponseModel.model_validate(p) for p in api_resp.json()]
        matching = [p for p in partners if p.code == partner_code]
        assert len(matching) == 1
        assert matching[0].name == partner_name
        assert matching[0].paymentTermsDays == 45

    @pytest.mark.negative_path
    def test_tc_ui_ak_04_unbalanced_journal_entry_blocked_and_balanced_posted(
        self,
        login_page: LoginPage,
        ledger_page: LedgerPage,
        accountant_client: ErpApiClient,
    ) -> None:
        """
        ID: TC-UI-AK-04 (Mirrors API Tests: TC-API-AK-07 [422 Unbalanced] & TC-API-AK-06 [Balanced Post])
        Owner: Aleksander Kazmierczak (251544)
        Priority: P0 (Critical)
        View / Component: `/ledger` -> `ManualEntryPanel` (Double-Entry Guard & Posting)
        Preconditions:
            - ERP backend and React SPA frontend are running.
            - User is authenticated in the UI as ACCOUNTANT (`accountant`).
            - Active GL accounts 1010 (Cash) and 3100 (Share Capital / Owner Equity) exist.
        Postconditions:
            - Entering asymmetric amounts (Debit 1010 = 100.00, Credit 3100 = 95.00) displays
              the red 'Unbalanced' badge and disables the 'Post entry' button.
            - Correcting the amounts to a balanced 350.00 / 350.00 switches the badge to
              'Balanced', enables 'Post entry', posts the journal entry, and preserves GL balance.
        """
        # Step 1: Log in as ACCOUNTANT and navigate to Ledger (/ledger)
        login_page.login_as_role(ErpRole.ACCOUNTANT)
        ledger_page.navigate_via_sidebar("Ledger")
        ledger_page.expect_pathname("/ledger")

        # Step 2: Enter an UNBALANCED journal entry (Debit 1010 = 100.00, Credit 3100 = 95.00)
        ledger_page.set_header_memo("TC-UI-AK-04 Double-entry UI guard verification")
        ledger_page.fill_journal_line(
            0,
            account_code="1010",
            debit="100.00",
            credit="0",
            line_memo="Debit leg 100.00",
        )
        ledger_page.fill_journal_line(
            1,
            account_code="3100",
            debit="0",
            credit="95.00",
            line_memo="Asymmetric credit leg 95.00",
        )

        # Step 3: Verify the UI displays the red 'Unbalanced' badge and disables 'Post entry'
        ledger_page.expect_unbalanced_state()

        # Step 4: Correct the lines to symmetric amounts (Debit = 350.00, Credit = 350.00)
        ledger_page.fill_journal_line(
            0,
            account_code="1010",
            debit="350.00",
            credit="0",
            line_memo="Balanced debit leg 350.00",
        )
        ledger_page.fill_journal_line(
            1,
            account_code="3100",
            debit="0",
            credit="350.00",
            line_memo="Balanced credit leg 350.00",
        )

        # Step 5: Verify the badge turns to 'Balanced', 'Post entry' is enabled, and submit
        ledger_page.expect_balanced_state()
        toast_text = ledger_page.submit_manual_entry_and_expect_posted()
        assert "posted" in toast_text.lower()

        # Step 6: Confirm via backend API that the General Ledger Trial Balance remains balanced
        tb = assert_valid_model(
            accountant_client.get("/api/ledger/trial-balance"),
            TrialBalanceReportModel,
            expected_status=200,
        )
        assert tb.balanced is True
        assert_decimal_equal(tb.totalDebit, tb.totalCredit, label="TrialBalance Debit==Credit")
        assert tb.totalDebit >= Decimal("350.0000")
