"""
Test module prepared for the second team member: Lukasz Murza (Student ID: 251592).

Demonstrates how to leverage the shared testing toolkit built according to DRY & SRP:
- pre-authenticated RBAC role client fixtures (`admin_client`, `accountant_client`,
  `warehouse_client`, `sales_client`, `guest_client`, `unauth_client`) from `tests/conftest.py`,
- `data_factory` (`TestDataFactory`) payload builders from `tests/factories.py`,
- shared assertion helpers (`assert_valid_model`, `assert_problem_detail`,
  `assert_decimal_equal`, `assert_status_code`) from `tests/assertions.py`,
- Pydantic contract models from `tests/models.py`.

How to run this suite (4x GET + 4x POST):
    python run_tests.py --suite lukasz
or:
    python -m pytest tests/test_api_lukasz.py
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.assertions import (
    assert_decimal_equal,
    assert_problem_detail,
    assert_status_code,
    assert_valid_model,
)
from tests.client import ErpApiClient
from tests.factories import TestDataFactory
from tests.models import (
    CurrentUserResponseModel,
    ItemResponseModel,
    PartnerResponseModel,
    PurchaseOrderResponseModel,
    SalesOrderResponseModel,
    TokenResponseModel,
    WarehouseResponseModel,
)


@pytest.mark.lukasz
@pytest.mark.get_method
@pytest.mark.happy_path
def test_luk_001_get_current_user_returns_authenticated_admin_profile(
    admin_client: ErpApiClient,
) -> None:
    """
    ID: LUK-001 | Author: Łukasz Murza | Priority: P1
    Category: authentication / contract validation / happy path
    Method: GET /api/auth/me
    """
    response = admin_client.get("/api/auth/me")
    current_user = assert_valid_model(response, CurrentUserResponseModel)

    assert current_user.username == "admin"
    assert set(current_user.roles) == {
        "ACCOUNTANT",
        "ADMIN",
        "HR",
        "SALES",
        "WAREHOUSE",
    }


@pytest.mark.lukasz
@pytest.mark.get_method
@pytest.mark.happy_path
def test_luk_002_get_inventory_on_hand_returns_consistent_stock_value(
    guest_client: ErpApiClient,
) -> None:
    """
    ID: LUK-002 | Author: Łukasz Murza | Priority: P1
    Category: inventory / data consistency / happy path
    Method: GET /api/inventory/items/{id}/on-hand
    """
    response = guest_client.get("/api/inventory/items/1/on-hand")
    assert_status_code(response, 200)
    assert "json" in response.headers.get("content-type", "").lower()

    body = response.json()
    assert set(body) == {"itemId", "sku", "onHandQty", "avgUnitCost", "totalValue"}
    assert body["itemId"] == 1
    assert body["sku"] == "RM-DEMO"
    assert_decimal_equal(body["onHandQty"], "100.000000", label="onHandQty")
    assert_decimal_equal(body["avgUnitCost"], "10.000000", label="avgUnitCost")
    assert_decimal_equal(body["totalValue"], "1000.0000", label="totalValue")
    assert_decimal_equal(
        body["totalValue"],
        Decimal(str(body["onHandQty"])) * Decimal(str(body["avgUnitCost"])),
        label="totalValue == onHandQty * avgUnitCost",
    )


@pytest.mark.lukasz
@pytest.mark.get_method
@pytest.mark.negative_path
def test_luk_003_get_item_by_unknown_sku_returns_problem_detail(
    guest_client: ErpApiClient,
) -> None:
    """
    ID: LUK-003 | Author: Łukasz Murza | Priority: P2
    Category: master data / negative lookup / error contract
    Method: GET /api/masterdata/items/by-sku
    """
    response = guest_client.get(
        "/api/masterdata/items/by-sku",
        params={"sku": "LUK-NONEXISTENT-SKU"},
    )
    problem = assert_problem_detail(
        response,
        expected_status=404,
        expected_title="Not Found",
    )
    assert problem.detail is not None
    assert "SKU" in problem.detail


@pytest.mark.lukasz
@pytest.mark.get_method
@pytest.mark.negative_path
def test_luk_004_get_current_user_without_token_returns_unauthorized(
    unauth_client: ErpApiClient,
) -> None:
    """
    ID: LUK-004 | Author: Łukasz Murza | Priority: P1
    Category: authentication / access control / negative path
    Method: GET /api/auth/me
    """
    response = unauth_client.get("/api/auth/me", authenticated=False)
    assert_problem_detail(
        response,
        expected_status=401,
        expected_title="Unauthorized",
        detail_contains="Authentication required",
    )


@pytest.mark.lukasz
@pytest.mark.post_method
@pytest.mark.happy_path
def test_luk_005_post_create_item_persists_master_data(
    admin_client: ErpApiClient,
    data_factory: type[TestDataFactory],
) -> None:
    """
    ID: LUK-005 | Author: Łukasz Murza | Priority: P1
    Category: master data / persistence / happy path
    Method: POST /api/masterdata/items
    """
    payload = data_factory.item_payload(
        name="Lukasz API Test Item",
        standard_cost="42.750000",
        reorder_point="7.000000",
        reorder_qty="21.000000",
    )
    created = assert_valid_model(
        admin_client.post("/api/masterdata/items", json=payload),
        ItemResponseModel,
        expected_status=201,
    )

    assert created.id > 0
    assert created.sku == payload["sku"]
    assert created.name == payload["name"]
    assert_decimal_equal(created.standardCost, payload["standardCost"], label="standardCost")
    assert_decimal_equal(created.reorderPoint, payload["reorderPoint"], label="reorderPoint")
    assert_decimal_equal(created.reorderQty, payload["reorderQty"], label="reorderQty")

    fetched = assert_valid_model(
        admin_client.get(f"/api/masterdata/items/{created.id}"),
        ItemResponseModel,
    )
    assert fetched.sku == created.sku
    assert fetched.id == created.id


@pytest.mark.lukasz
@pytest.mark.post_method
@pytest.mark.happy_path
def test_luk_006_post_create_warehouse_returns_active_resource(
    admin_client: ErpApiClient,
    data_factory: type[TestDataFactory],
) -> None:
    """
    ID: LUK-006 | Author: Łukasz Murza | Priority: P2
    Category: master data / resource creation / happy path
    Method: POST /api/masterdata/warehouses
    """
    payload = data_factory.warehouse_payload(name="Lukasz Test Warehouse")
    created = assert_valid_model(
        admin_client.post("/api/masterdata/warehouses", json=payload),
        WarehouseResponseModel,
        expected_status=201,
    )

    assert created.id > 0
    assert created.code == payload["code"]
    assert created.name == payload["name"]
    assert created.active is True

    warehouses = admin_client.get("/api/masterdata/warehouses")
    assert_status_code(warehouses, 200)
    assert any(row["id"] == created.id and row["code"] == created.code for row in warehouses.json())


@pytest.mark.lukasz
@pytest.mark.post_method
@pytest.mark.negative_path
def test_luk_007_post_purchase_order_for_unknown_partner_returns_404(
    warehouse_client: ErpApiClient,
    data_factory: type[TestDataFactory],
) -> None:
    """
    ID: LUK-007 | Author: Łukasz Murza | Priority: P1
    Category: purchasing / referential integrity / negative path
    Method: POST /api/purchasing/purchase-orders
    """
    payload = data_factory.purchase_order_payload(partner_id=999999999, item_id=1)
    response = warehouse_client.post("/api/purchasing/purchase-orders", json=payload)
    problem = assert_problem_detail(
        response,
        expected_status=404,
        expected_title="Not Found",
    )
    assert problem.detail is not None
    assert "Partner" in problem.detail


@pytest.mark.lukasz
@pytest.mark.post_method
@pytest.mark.negative_path
def test_luk_008_post_login_with_invalid_credentials_is_rejected(
    unauth_client: ErpApiClient,
) -> None:
    """
    ID: LUK-008 | Author: Łukasz Murza | Priority: P1
    Category: authentication / negative path / error contract
    Method: POST /api/auth/login
    """
    response = unauth_client.login("lukasz-invalid-user", "wrong-password")
    assert_problem_detail(
        response,
        expected_status=401,
        expected_title="Unauthorized",
        detail_contains="Invalid username or password",
    )

__all__ = [
    "pytest",
    "ErpApiClient",
    "TestDataFactory",
    "assert_valid_model",
    "assert_problem_detail",
    "assert_decimal_equal",
    "assert_status_code",
    "CurrentUserResponseModel",
    "ItemResponseModel",
    "PartnerResponseModel",
    "PurchaseOrderResponseModel",
    "SalesOrderResponseModel",
    "TokenResponseModel",
    "WarehouseResponseModel",
]
