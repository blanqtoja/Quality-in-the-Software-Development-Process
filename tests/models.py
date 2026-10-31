"""
Pydantic contract models (SRP) for validating JSON payloads returned by the REST API.

All monetary amounts and quantities are validated as Decimal (serialized as JSON strings
by JacksonConfig.java in the Spring Boot backend).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetailModel(BaseModel):
    """RFC 9457 Problem Details error response model (application/problem+json)."""

    model_config = ConfigDict(extra="allow")

    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None


class TokenResponseModel(BaseModel):
    """Response model for POST /api/auth/login and POST /api/auth/refresh."""

    accessToken: str
    username: str
    roles: list[str]


class CurrentUserResponseModel(BaseModel):
    """Response model for GET /api/auth/me."""

    username: str
    roles: list[str]


class ItemResponseModel(BaseModel):
    """Response model for /api/masterdata/items endpoints."""

    id: int
    sku: str
    name: str
    itemType: str
    uom: str
    stocked: bool
    standardCost: Decimal
    reorderPoint: Decimal
    reorderQty: Decimal


class PartnerResponseModel(BaseModel):
    """Response model for /api/masterdata/partners endpoints."""

    id: int
    code: str
    name: str
    vendor: bool
    customer: bool
    taxId: Optional[str] = None
    paymentTermsDays: int
    apAccountCode: Optional[str] = None
    arAccountCode: Optional[str] = None
    active: bool


class WarehouseResponseModel(BaseModel):
    """Response model for /api/masterdata/warehouses endpoints."""

    id: int
    code: str
    name: str
    active: bool


class JournalEntryResponseModel(BaseModel):
    """Response model for POST /api/ledger/journal-entries."""

    id: int
    entryNo: int
    status: str
    postingDate: date
    currencyCode: str
    totalDebit: Decimal
    totalCredit: Decimal


class SubledgerCheckModel(BaseModel):
    """Single subledger reconciliation entry compared against its GL control account."""

    label: str
    accountCode: str
    subledger: Decimal
    glControl: Decimal
    reconciled: bool


class ClearingBalanceModel(BaseModel):
    """Transitional clearing account balance (GR-IR, Deferred-COGS, WIP)."""

    accountCode: str
    name: str
    balance: Decimal
    cleared: bool


class ReconciliationReportModel(BaseModel):
    """Response model for GET /api/reporting/reconciliation (Hero Check)."""

    asOf: date
    healthy: bool
    trialBalanceBalanced: bool
    subledgerChecks: list[SubledgerCheckModel]
    clearingAccounts: list[ClearingBalanceModel]


class TrialBalanceLineModel(BaseModel):
    """Single line of the General Ledger trial balance."""

    model_config = ConfigDict(extra="allow")

    accountCode: str
    accountName: str
    debit: Decimal
    credit: Decimal


class TrialBalanceReportModel(BaseModel):
    """Response model for GET /api/ledger/trial-balance."""

    lines: list[TrialBalanceLineModel]
    totalDebit: Decimal
    totalCredit: Decimal
    balanced: bool


class SoLineViewModel(BaseModel):
    """Sales Order line item view."""

    id: int
    lineNo: int
    itemId: int
    qtyOrdered: Decimal
    qtyShipped: Decimal
    qtyInvoiced: Decimal
    unitPrice: Decimal


class SalesOrderResponseModel(BaseModel):
    """Response model for /api/sales/sales-orders endpoints."""

    id: int
    soNumber: str
    partnerId: int
    orderDate: date
    status: str
    lines: list[SoLineViewModel]


class PoLineViewModel(BaseModel):
    """Purchase Order line item view."""

    id: int
    lineNo: int
    itemId: int
    qtyOrdered: Decimal
    qtyReceived: Decimal
    qtyBilled: Decimal
    unitPrice: Decimal


class PurchaseOrderResponseModel(BaseModel):
    """Response model for /api/purchasing/purchase-orders endpoints."""

    id: int
    poNumber: str
    partnerId: int
    orderDate: date
    status: str
    lines: list[PoLineViewModel]
