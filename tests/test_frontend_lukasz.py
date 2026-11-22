"""Frontend UI suite for Lukasz Murza (251592), using the team's pytest/POM stack.

TC-UI-LM-01..04 cover partner read permissions, missing-entry reversal handling,
purchase-order validation, and trial-balance presentation. Aleksander's existing
tests remain in tests/test_frontend_aleksander.py.
"""

from __future__ import annotations

import pytest

from tests.assertions import assert_problem_detail
from tests.client import ErpApiClient
from tests.config import ErpRole
from tests.models import PartnerResponseModel
from tests.pages import LedgerPage, LoginPage, MasterDataPage, PurchasingPage, ReportingPage


@pytest.mark.lukasz
@pytest.mark.frontend
class TestFrontendLukasz:
    @pytest.mark.negative_path
    def test_tc_ui_lm_01_guest_reads_partner_without_create_action(
        self, login_page: LoginPage, master_data_page: MasterDataPage,
        guest_client: ErpApiClient,
    ) -> None:
        """TC-UI-LM-01 | SC-IAM-01 | P1 | Read a concrete partner as GUEST.

        Preconditions: a seeded partner exists; GUEST may read master data.
        Expected: the code and name from GET are visible, creation is unavailable.
        """
        response = guest_client.get("/api/masterdata/partners")
        assert response.status_code == 200
        partners = response.json()
        assert partners, "Seed at least one partner before running TC-UI-LM-01"
        partner = PartnerResponseModel.model_validate(partners[0])
        login_page.login_as_role(ErpRole.GUEST)
        master_data_page.open().open_partners_tab()
        master_data_page.expect_partner_read_only(code=partner.code, name=partner.name)

    @pytest.mark.negative_path
    def test_tc_ui_lm_02_missing_reversal_entry_shows_error_without_write(
        self, login_page: LoginPage, ledger_page: LedgerPage,
        accountant_client: ErpApiClient,
    ) -> None:
        """TC-UI-LM-02 | SC-GL-03 | P1 | A nonexistent entry cannot be reversed.

        Preconditions: entry 999999999 does not exist; ACCOUNTANT can use Reversal.
        Expected: GET returns 404, UI reports the missing entry, no reversal form
        or ledger POST is produced. This does not repeat the manual-entry guard.
        """
        missing_entry_no = 999_999_999
        assert_problem_detail(
            accountant_client.get(f"/api/ledger/journal-entries/{missing_entry_no}"),
            expected_status=404, expected_title="Not Found",
        )
        login_page.login_as_role(ErpRole.ACCOUNTANT)
        ledger_page.open().open_reversal_tab()
        with ledger_page.record_post_requests("/api/ledger/") as writes:
            ledger_page.load_missing_reversal_entry(missing_entry_no)
            assert not writes, "Loading a nonexistent entry must not post to the ledger"

    @pytest.mark.negative_path
    def test_tc_ui_lm_03_purchase_order_requires_complete_line(
        self, login_page: LoginPage, purchasing_page: PurchasingPage,
        warehouse_client: ErpApiClient,
    ) -> None:
        """TC-UI-LM-03 | SC-P2P-01 | P1 | Reject an incomplete purchase order.

        Preconditions: WAREHOUSE account and at least one existing vendor.
        Expected: a visible validation message, modal remains open, no create POST.
        """
        response = warehouse_client.get("/api/masterdata/partners", params={"vendor": "true"})
        assert response.status_code == 200
        vendors = [PartnerResponseModel.model_validate(row) for row in response.json() if row["vendor"]]
        assert vendors, "Seed a vendor before running TC-UI-LM-03"
        login_page.login_as_role(ErpRole.WAREHOUSE)
        purchasing_page.open()
        modal = purchasing_page.open_order_with_vendor(vendors[0].code)
        with purchasing_page.record_post_requests("/api/purchasing/purchase-orders") as writes:
            purchasing_page.submit_incomplete_order(modal)
            assert not writes, "An incomplete order must be rejected before the create request"

    @pytest.mark.happy_path
    def test_tc_ui_lm_04_trial_balance_matches_api_presentation(
        self, login_page: LoginPage, reporting_page: ReportingPage,
    ) -> None:
        """TC-UI-LM-04 | SC-REP-01 | P1 | Display trial-balance API values.

        Coverage is limited to the trial-balance table, totals and balance badge;
        subledger reconciliation in Dashboard is covered by TC-UI-AK-01.
        """
        login_page.login_as_role(ErpRole.ACCOUNTANT)
        reporting_page.expect_trial_balance_matches_api()
