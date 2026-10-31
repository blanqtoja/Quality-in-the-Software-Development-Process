"""
Test data factory (TestDataFactory) following the DRY principle.

Generates unique, deterministic JSON request payloads for ERP modules
(masterdata, ledger, sales, purchasing, inventory, hr). Unique suffixes ensure
tests are idempotent and can be executed repeatedly without 409 Conflict errors.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Optional


class TestDataFactory:
    """Reusable REST API request payload builder for both team members."""

    @staticmethod
    def unique_code(prefix: str) -> str:
        """Generates a short unique alphanumeric code, e.g. 'ITM-A1B2C3D4'."""
        suffix = uuid.uuid4().hex[:8].upper()
        return f"{prefix}-{suffix}"

    @classmethod
    def item_payload(
        cls,
        *,
        sku: Optional[str] = None,
        name: str = "Test Raw Material Steel S235",
        item_type: str = "RAW_MATERIAL",
        uom: str = "PCS",
        stocked: bool = True,
        standard_cost: str | Decimal = "25.500000",
        reorder_point: str | Decimal = "10.000000",
        reorder_qty: str | Decimal = "50.000000",
    ) -> dict[str, Any]:
        """Builds a JSON payload for POST /api/masterdata/items."""
        return {
            "sku": sku or cls.unique_code("ITM"),
            "name": name,
            "itemType": item_type,
            "uom": uom,
            "stocked": stocked,
            "standardCost": str(standard_cost),
            "reorderPoint": str(reorder_point),
            "reorderQty": str(reorder_qty),
        }

    @classmethod
    def partner_payload(
        cls,
        *,
        code: Optional[str] = None,
        name: str = "Test Business Partner Ltd.",
        vendor: bool = True,
        customer: bool = True,
        tax_id: str = "PL5260001234",
        payment_terms_days: int = 30,
        ap_account_code: str = "2100",
        ar_account_code: str = "1200",
    ) -> dict[str, Any]:
        """Builds a JSON payload for POST /api/masterdata/partners."""
        return {
            "code": code or cls.unique_code("PRT"),
            "name": name,
            "vendor": vendor,
            "customer": customer,
            "taxId": tax_id,
            "paymentTermsDays": payment_terms_days,
            "apAccountCode": ap_account_code,
            "arAccountCode": ar_account_code,
        }

    @classmethod
    def warehouse_payload(
        cls,
        *,
        code: Optional[str] = None,
        name: str = "Central Test Warehouse",
    ) -> dict[str, Any]:
        """Builds a JSON payload for POST /api/masterdata/warehouses."""
        return {
            "code": code or cls.unique_code("WH"),
            "name": name,
        }

    @staticmethod
    def journal_entry_payload(
        *,
        posting_date: str = "2026-06-15",
        memo: str = "Automated API test journal entry",
        debit_account: str = "1010",
        credit_account: str = "3100",
        debit_amount: str | Decimal = "250.0000",
        credit_amount: str | Decimal = "250.0000",
        currency_code: str = "TWD",
    ) -> dict[str, Any]:
        """
        Builds a JSON payload for POST /api/ledger/journal-entries.
        When debit_amount == credit_amount -> balanced entry (Happy Path).
        When debit_amount != credit_amount -> unbalanced entry (Negative Path).
        """
        return {
            "journalCode": "GEN",
            "postingDate": posting_date,
            "memo": memo,
            "currencyCode": currency_code,
            "lines": [
                {
                    "accountCode": debit_account,
                    "debit": str(debit_amount),
                    "credit": "0.0000",
                    "memo": f"Debit leg on account {debit_account}",
                },
                {
                    "accountCode": credit_account,
                    "debit": "0.0000",
                    "credit": str(credit_amount),
                    "memo": f"Credit leg on account {credit_account}",
                },
            ],
        }

    @staticmethod
    def sales_order_payload(
        *,
        partner_id: int,
        item_id: int,
        qty_ordered: str | Decimal = "5.000000",
        unit_price: str | Decimal = "120.0000",
        order_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """Builds a JSON payload for POST /api/sales/sales-orders."""
        return {
            "partnerId": partner_id,
            "orderDate": order_date or date(2026, 6, 15).isoformat(),
            "lines": [
                {
                    "itemId": item_id,
                    "qtyOrdered": str(qty_ordered),
                    "unitPrice": str(unit_price),
                }
            ],
        }

    @staticmethod
    def purchase_order_payload(
        *,
        partner_id: int,
        item_id: int,
        qty_ordered: str | Decimal = "20.000000",
        unit_price: str | Decimal = "15.0000",
        order_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """Builds a JSON payload for POST /api/purchasing/purchase-orders."""
        return {
            "partnerId": partner_id,
            "orderDate": order_date or date(2026, 6, 15).isoformat(),
            "lines": [
                {
                    "itemId": item_id,
                    "qtyOrdered": str(qty_ordered),
                    "unitPrice": str(unit_price),
                }
            ],
        }
