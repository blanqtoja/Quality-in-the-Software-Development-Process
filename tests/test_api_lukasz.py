"""
Test module prepared for the second team member: Lukasz Murza (Student ID: 251592).

Demonstrates how to leverage the shared testing toolkit built according to DRY & SRP:
- pre-authenticated RBAC role client fixtures (`admin_client`, `accountant_client`,
  `warehouse_client`, `sales_client`, `guest_client`, `unauth_client`) from `tests/conftest.py`,
- `data_factory` (`TestDataFactory`) payload builders from `tests/factories.py`,
- shared assertion helpers (`assert_valid_model`, `assert_problem_detail`,
  `assert_decimal_equal`, `assert_status_code`) from `tests/assertions.py`,
- Pydantic contract models from `tests/models.py`.

How to run this suite once populated with 8 tests (4x GET + 4x POST):
    python run_tests.py --suite lukasz
or:
    python -m pytest tests/test_api_lukasz.py
"""

from __future__ import annotations

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
