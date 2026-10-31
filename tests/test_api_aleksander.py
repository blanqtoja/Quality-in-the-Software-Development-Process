"""
Suite of 8 automated REST API tests for the Manufacturing ERP system.
Owner: Aleksander Kazmierczak (Student ID: 251544).

Test distribution per course requirements:
- Because the ERP REST API exposes only GET and POST endpoints (immutable append-only
  ledger and documents — no PUT/DELETE), this suite contains 8 distinct test cases
  evenly split across the available HTTP methods:
  * 4 tests for HTTP GET  (2x Happy Path, 2x Negative Path)
  * 4 tests for HTTP POST (2x Happy Path, 2x Negative Path)
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.assertions import (
    assert_decimal_equal,
    assert_problem_detail,
    assert_valid_model,
)
from tests.client import ErpApiClient
from tests.factories import TestDataFactory
from tests.models import (
    ItemResponseModel,
    JournalEntryResponseModel,
    PartnerResponseModel,
    ReconciliationReportModel,
    TrialBalanceReportModel,
)


@pytest.mark.aleksander
@pytest.mark.get_method
class TestGetEndpointsAleksander:
    """Tests verifying HTTP GET endpoints (2x Happy Path, 2x Negative Path)."""

    @pytest.mark.happy_path
    def test_tc_api_ak_01_get_reconciliation_report_happy_path(
        self,
        accountant_client: ErpApiClient,
    ) -> None:
        """
        ID: TC-API-AK-01
        Owner: Aleksander Kazmierczak (251544)
        Priority: P0 (Critical)
        Method / Endpoint: GET /api/reporting/reconciliation (Happy Path)
        Preconditions:
            - Manufacturing ERP REST API server is running.
            - Client is authenticated with a valid JWT token for role ACCOUNTANT.
        Postconditions:
            - Returns HTTP 200 OK and a valid reconciliation report JSON payload.
            - Flags healthy == True and trialBalanceBalanced == True.
            - Database state remains unchanged (read-only idempotent operation).
        """
        # Step 1: Send GET /api/reporting/reconciliation with ACCOUNTANT bearer token
        response = accountant_client.get("/api/reporting/reconciliation")

        # Step 2: Verify HTTP 200 OK and validate schema using ReconciliationReportModel
        report = assert_valid_model(response, ReconciliationReportModel, expected_status=200)

        # Step 3: Verify headline accounting invariants
        assert report.healthy is True, "Reconciliation report must indicate healthy=True"
        assert report.trialBalanceBalanced is True, "Trial balance must be balanced"
        assert len(report.subledgerChecks) > 0, "Subledger checks list must not be empty"

        # Step 4: Verify that every subledger reconciles with its GL control account (Decimal)
        for check in report.subledgerChecks:
            assert check.reconciled is True, f"Subledger {check.label} ({check.accountCode}) is not reconciled"
            assert_decimal_equal(check.subledger, check.glControl, label=f"Subledger vs GL ({check.accountCode})")

    @pytest.mark.happy_path
    def test_tc_api_ak_02_get_item_by_sku_happy_path(
        self,
        admin_client: ErpApiClient,
        seeded_item: ItemResponseModel,
    ) -> None:
        """
        ID: TC-API-AK-02
        Owner: Aleksander Kazmierczak (251544)
        Priority: P1 (High)
        Method / Endpoint: GET /api/masterdata/items/by-sku?sku={sku} (Happy Path)
        Preconditions:
            - ERP REST API server is running.
            - A test item with a known unique SKU exists in the system (seeded_item fixture).
            - Client is authenticated with a valid JWT token.
        Postconditions:
            - Returns HTTP 200 OK.
            - Returned item attributes match the seeded record (id, sku, standardCost).
        """
        # Step 1: Send GET /api/masterdata/items/by-sku with the item's SKU query parameter
        response = admin_client.get("/api/masterdata/items/by-sku", params={"sku": seeded_item.sku})

        # Step 2: Verify HTTP 200 OK and validate payload against ItemResponseModel
        fetched_item = assert_valid_model(response, ItemResponseModel, expected_status=200)

        # Step 3: Compare returned fields against the seeded item record
        assert fetched_item.id == seeded_item.id
        assert fetched_item.sku == seeded_item.sku
        assert fetched_item.name == seeded_item.name
        assert fetched_item.itemType == seeded_item.itemType
        assert_decimal_equal(fetched_item.standardCost, seeded_item.standardCost, label="standardCost")

    @pytest.mark.negative_path
    def test_tc_api_ak_03_get_nonexistent_item_by_id_returns_404(
        self,
        guest_client: ErpApiClient,
    ) -> None:
        """
        ID: TC-API-AK-03
        Owner: Aleksander Kazmierczak (251544)
        Priority: P2 (Medium)
        Method / Endpoint: GET /api/masterdata/items/{id} (Negative Path - 404 Not Found)
        Preconditions:
            - ERP REST API server is running.
            - Client is authenticated with role GUEST.
            - Item ID 999999999 does not exist in the masterdata item table.
        Postconditions:
            - Returns HTTP 404 Not Found.
            - Error payload conforms to RFC 9457 (application/problem+json) with status=404.
        """
        non_existent_id = 999_999_999

        # Step 1: Send GET request for a non-existent item ID
        response = guest_client.get(f"/api/masterdata/items/{non_existent_id}")

        # Step 2: Verify RFC 9457 Problem Details error contract (404 Not Found)
        problem = assert_problem_detail(
            response,
            expected_status=404,
            expected_title="Not Found",
        )

        # Step 3: Ensure diagnostic detail message is present
        assert problem.detail is not None and len(problem.detail) > 0

    @pytest.mark.negative_path
    def test_tc_api_ak_04_get_audit_log_as_guest_returns_403_forbidden(
        self,
        guest_client: ErpApiClient,
    ) -> None:
        """
        ID: TC-API-AK-04
        Owner: Aleksander Kazmierczak (251544)
        Priority: P1 (High)
        Method / Endpoint: GET /api/audit (Negative Path - 403 Forbidden RBAC)
        Preconditions:
            - ERP REST API server is running with Spring Security RBAC active.
            - Client is authenticated as 'guest' (lacks ROLE_ADMIN authority).
        Postconditions:
            - Access to the audit trail is denied with HTTP 403 Forbidden.
            - RFC 9457 ProblemDetail response confirms insufficient permissions.
        """
        # Step 1: Send GET /api/audit using a GUEST role JWT token
        response = guest_client.get("/api/audit")

        # Step 2: Verify RBAC rejection (HTTP 403 Forbidden in problem+json format)
        assert_problem_detail(
            response,
            expected_status=403,
            expected_title="Forbidden",
            detail_contains="permission",
        )


@pytest.mark.aleksander
@pytest.mark.post_method
class TestPostEndpointsAleksander:
    """Tests verifying HTTP POST endpoints (2x Happy Path, 2x Negative Path)."""

    @pytest.mark.happy_path
    def test_tc_api_ak_05_post_create_partner_happy_path(
        self,
        admin_client: ErpApiClient,
        data_factory: type[TestDataFactory],
    ) -> None:
        """
        ID: TC-API-AK-05
        Owner: Aleksander Kazmierczak (251544)
        Priority: P1 (High)
        Method / Endpoint: POST /api/masterdata/partners (Happy Path)
        Preconditions:
            - ERP REST API server is running.
            - Client is authenticated with role ADMIN (authorized for masterdata writes).
            - Unique partner code generated via TestDataFactory.
        Postconditions:
            - Returns HTTP 201 Created.
            - New partner has a generated ID, active=True, and is retrievable via GET.
        """
        # Step 1: Build a valid CreatePartnerRequest payload using TestDataFactory
        payload = data_factory.partner_payload(
            name="Lodz University of Technology Test Supplier",
            vendor=True,
            customer=True,
            payment_terms_days=45,
        )

        # Step 2: Send POST /api/masterdata/partners as ADMIN
        create_resp = admin_client.post("/api/masterdata/partners", json=payload)

        # Step 3: Verify HTTP 201 Created and validate PartnerResponseModel schema
        created = assert_valid_model(create_resp, PartnerResponseModel, expected_status=201)
        assert created.id > 0
        assert created.code == payload["code"]
        assert created.name == payload["name"]
        assert created.vendor is True
        assert created.customer is True
        assert created.paymentTermsDays == 45
        assert created.active is True

        # Step 4: Verify persistence postcondition via GET /api/masterdata/partners/{id}
        get_resp = admin_client.get(f"/api/masterdata/partners/{created.id}")
        fetched = assert_valid_model(get_resp, PartnerResponseModel, expected_status=200)
        assert fetched.code == created.code

    @pytest.mark.happy_path
    def test_tc_api_ak_06_post_balanced_journal_entry_happy_path(
        self,
        accountant_client: ErpApiClient,
        data_factory: type[TestDataFactory],
    ) -> None:
        """
        ID: TC-API-AK-06
        Owner: Aleksander Kazmierczak (251544)
        Priority: P0 (Critical)
        Method / Endpoint: POST /api/ledger/journal-entries (Happy Path)
        Preconditions:
            - ERP REST API server is running.
            - Client is authenticated with role ACCOUNTANT.
            - Open fiscal period in FY2026 and active GL accounts 1010 and 3100.
        Postconditions:
            - Returns HTTP 201 Created.
            - Entry is marked POSTED with totalDebit == totalCredit == 350.0000.
            - General Ledger trial balance remains balanced (balanced == True).
        """
        # Step 1: Build a balanced journal entry payload (Dt 1010 = 350.0000, Ct 3100 = 350.0000)
        payload = data_factory.journal_entry_payload(
            posting_date="2026-06-15",
            memo="TC-API-AK-06 Balanced manual journal entry",
            debit_account="1010",
            credit_account="3100",
            debit_amount=Decimal("350.0000"),
            credit_amount=Decimal("350.0000"),
        )

        # Step 2: Send POST /api/ledger/journal-entries as ACCOUNTANT
        response = accountant_client.post("/api/ledger/journal-entries", json=payload)

        # Step 3: Verify HTTP 201 Created and exact Decimal amounts
        entry = assert_valid_model(response, JournalEntryResponseModel, expected_status=201)
        assert entry.status == "POSTED"
        assert entry.entryNo > 0
        assert_decimal_equal(entry.totalDebit, Decimal("350.0000"), label="totalDebit")
        assert_decimal_equal(entry.totalCredit, Decimal("350.0000"), label="totalCredit")

        # Step 4: Verify trial balance postcondition (GET /api/ledger/trial-balance)
        tb_resp = accountant_client.get("/api/ledger/trial-balance")
        tb = assert_valid_model(tb_resp, TrialBalanceReportModel, expected_status=200)
        assert tb.balanced is True
        assert_decimal_equal(tb.totalDebit, tb.totalCredit, label="TrialBalance Debit==Credit")

    @pytest.mark.negative_path
    def test_tc_api_ak_07_post_unbalanced_journal_entry_rejected(
        self,
        accountant_client: ErpApiClient,
        data_factory: type[TestDataFactory],
    ) -> None:
        """
        ID: TC-API-AK-07
        Owner: Aleksander Kazmierczak (251544)
        Priority: P0 (Critical)
        Method / Endpoint: POST /api/ledger/journal-entries (Negative Path - 422 Unprocessable Entity)
        Preconditions:
            - ERP REST API server is running.
            - Client is authenticated with role ACCOUNTANT.
        Postconditions:
            - Asymmetric journal entry (Debit=100.0000 != Credit=95.0000) is rejected with HTTP 422.
            - Transaction is rolled back and General Ledger trial balance totals remain unchanged.
        """
        # Step 1: Record the trial balance totals prior to attempting the invalid post
        tb_before = assert_valid_model(
            accountant_client.get("/api/ledger/trial-balance"),
            TrialBalanceReportModel,
            expected_status=200,
        )

        # Step 2: Build an unbalanced journal entry payload (discrepancy of 5.0000)
        unbalanced_payload = data_factory.journal_entry_payload(
            posting_date="2026-06-15",
            memo="TC-API-AK-07 Unbalanced journal entry",
            debit_account="1010",
            credit_account="4100",
            debit_amount=Decimal("100.0000"),
            credit_amount=Decimal("95.0000"),
        )

        # Step 3: Send POST /api/ledger/journal-entries and verify HTTP 422 rejection
        response = accountant_client.post("/api/ledger/journal-entries", json=unbalanced_payload)
        assert_problem_detail(
            response,
            expected_status=422,
            expected_title="Unprocessable Entity",
        )

        # Step 4: Verify rollback postcondition - GL trial balance totals are untouched
        tb_after = assert_valid_model(
            accountant_client.get("/api/ledger/trial-balance"),
            TrialBalanceReportModel,
            expected_status=200,
        )
        assert tb_after.balanced is True
        assert_decimal_equal(tb_after.totalDebit, tb_before.totalDebit, label="Unchanged totalDebit after rollback")
        assert_decimal_equal(tb_after.totalCredit, tb_before.totalCredit, label="Unchanged totalCredit after rollback")

    @pytest.mark.negative_path
    def test_tc_api_ak_08_post_sales_order_empty_body_returns_400_bad_request(
        self,
        sales_client: ErpApiClient,
    ) -> None:
        """
        ID: TC-API-AK-08
        Owner: Aleksander Kazmierczak (251544)
        Priority: P2 (Medium)
        Method / Endpoint: POST /api/sales/sales-orders (Negative Path - 400 Bad Request)
        Preconditions:
            - ERP REST API server is running.
            - Client is authenticated with role SALES.
        Postconditions:
            - Sending an empty JSON object {} missing required fields (@NotNull partnerId,
              orderDate, @NotEmpty lines) returns HTTP 400 Bad Request in RFC 9457 format.
            - No sales order record is created.
        """
        # Step 1: Send an incomplete POST /api/sales/sales-orders request with an empty body {}
        response = sales_client.post("/api/sales/sales-orders", json={})

        # Step 2: Verify HTTP 400 Bad Request and RFC 9457 ProblemDetail contract
        problem = assert_problem_detail(
            response,
            expected_status=400,
            expected_title="Bad Request",
        )

        # Step 3: Confirm validation failure details are included in the response
        assert problem.detail is not None and len(problem.detail) > 0
