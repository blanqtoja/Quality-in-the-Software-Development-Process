"""
Built-in local reference REST API engine for the Manufacturing ERP system
with an httpx.BaseTransport adapter.

Activated automatically by the session fixture in conftest.py ONLY when an
external Docker / Spring Boot container (at ERP_BASE_URL, e.g. http://localhost:8081)
is not currently running. Mirrors the Spring Boot controllers 1:1:
- JWT authentication and RBAC role matrix from SecurityConfig.java,
- RFC 9457 (application/problem+json) error format from GlobalExceptionHandler.java,
- domain rules for modules: auth, masterdata, ledger, reporting, sales, purchasing, inventory, audit.
"""

from __future__ import annotations

import json
import re
import threading
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from urllib.parse import parse_qs

import httpx

from tests.config import ROLE_ACCOUNTS


class ErpReferenceState:
    """In-memory state of the reference ERP engine (seeded like DataSeeder.java)."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.tokens: dict[str, tuple[str, list[str]]] = {}
        self.accounts: dict[str, str] = {
            "1010": "Cash / Bank",
            "1200": "Accounts Receivable",
            "1310": "Inventory - Raw Materials",
            "1320": "Work-In-Process (WIP)",
            "1330": "Inventory - Finished Goods",
            "1450": "Input VAT",
            "2100": "Accounts Payable",
            "2150": "GR-IR Clearing",
            "2400": "Output VAT Payable",
            "3100": "Share Capital",
            "3200": "Retained Earnings",
            "4100": "Sales Revenue",
            "5100": "COGS",
            "5930": "Manufacturing Variance",
            "6000": "Inventory Adjustment / Loss",
            "9990": "Rounding Difference",
        }
        self.items: dict[int, dict[str, Any]] = {
            1: {
                "id": 1,
                "sku": "RM-DEMO",
                "name": "Demo Raw Material",
                "itemType": "RAW_MATERIAL",
                "uom": "PCS",
                "stocked": True,
                "standardCost": "10.000000",
                "reorderPoint": "20.000000",
                "reorderQty": "100.000000",
            },
            2: {
                "id": 2,
                "sku": "FG-DEMO",
                "name": "Demo Finished Good",
                "itemType": "FINISHED_GOOD",
                "uom": "PCS",
                "stocked": True,
                "standardCost": "50.000000",
                "reorderPoint": "10.000000",
                "reorderQty": "50.000000",
            },
        }
        self.partners: dict[int, dict[str, Any]] = {
            1: {
                "id": 1,
                "code": "VEND-DEMO",
                "name": "Demo Vendor Co.",
                "vendor": True,
                "customer": False,
                "taxId": "TW12345678",
                "paymentTermsDays": 30,
                "apAccountCode": "2100",
                "arAccountCode": None,
                "active": True,
            },
            2: {
                "id": 2,
                "code": "CUST-DEMO",
                "name": "Demo Customer Ltd.",
                "vendor": False,
                "customer": True,
                "taxId": "TW87654321",
                "paymentTermsDays": 30,
                "apAccountCode": None,
                "arAccountCode": "1200",
                "active": True,
            },
        }
        self.warehouses: dict[int, dict[str, Any]] = {
            1: {"id": 1, "code": "WH1", "name": "Main Warehouse", "active": True}
        }
        self.journal_entries: dict[int, dict[str, Any]] = {
            1: {
                "id": 1,
                "entryNo": 1,
                "status": "POSTED",
                "postingDate": "2026-01-15",
                "currencyCode": "TWD",
                "memo": "Opening seed entry",
                "sourceDocType": None,
                "sourceDocId": None,
                "reversesEntryNo": None,
                "reversedByEntryNo": None,
                "totalDebit": "1000.0000",
                "totalCredit": "1000.0000",
                "lines": [
                    {
                        "accountCode": "1010",
                        "accountName": "Cash / Bank",
                        "debit": "1000.0000",
                        "credit": "0.0000",
                        "memo": "Initial cash",
                        "partnerId": None,
                    },
                    {
                        "accountCode": "3100",
                        "accountName": "Share Capital",
                        "debit": "0.0000",
                        "credit": "1000.0000",
                        "memo": "Initial equity",
                        "partnerId": None,
                    },
                ],
            }
        }
        self.sales_orders: dict[int, dict[str, Any]] = {}
        self.purchase_orders: dict[int, dict[str, Any]] = {}
        self.audit_logs: list[dict[str, Any]] = [
            {
                "id": 1,
                "eventType": "AUTH_LOGIN_SUCCESS",
                "actor": "seed",
                "summary": "Initial system seed",
                "occurredAt": datetime.now(timezone.utc).isoformat(),
            }
        ]


class ErpReferenceTransport(httpx.BaseTransport):
    """
    HTTPX custom transport implementing the Spring Boot ERPSystem REST contract.
    Enables full HTTPX request/response testing even when Docker is not running.
    """

    def __init__(self, state: Optional[ErpReferenceState] = None) -> None:
        self.state = state or ErpReferenceState()

    @staticmethod
    def _json_response(
        status: int,
        payload: Any,
        content_type: str = "application/json",
        extra_headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        headers = {"Content-Type": content_type}
        if extra_headers:
            headers.update(extra_headers)
        return httpx.Response(
            status_code=status,
            headers=headers,
            content=json.dumps(payload).encode("utf-8"),
        )

    @classmethod
    def _problem_response(cls, status: int, title: str, detail: str) -> httpx.Response:
        return cls._json_response(
            status,
            {
                "type": "about:blank",
                "title": title,
                "status": status,
                "detail": detail,
            },
            content_type="application/problem+json",
        )

    def _authenticate(self, request: httpx.Request) -> Optional[tuple[str, list[str]]]:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.removeprefix("Bearer ").strip()
        return self.state.tokens.get(token)

    def _require_auth(
        self,
        request: httpx.Request,
        required_roles: Optional[set[str]] = None,
    ) -> tuple[Optional[tuple[str, list[str]]], Optional[httpx.Response]]:
        principal = self._authenticate(request)
        if principal is None:
            return None, self._problem_response(401, "Unauthorized", "Authentication required")
        username, roles = principal
        if required_roles is not None and not (set(roles) & required_roles):
            return None, self._problem_response(
                403, "Forbidden", "You do not have permission to perform this action"
            )
        return (username, roles), None

    @staticmethod
    def _parse_body(request: httpx.Request) -> Optional[dict[str, Any]]:
        raw = request.read()
        if not raw:
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        path = request.url.path
        query = parse_qs(request.url.query.decode("utf-8"))

        if method == "GET":
            return self._handle_get(request, path, query)
        if method == "POST":
            return self._handle_post(request, path)
        return self._problem_response(405, "Method Not Allowed", f"Unsupported HTTP method: {method}")

    def _handle_get(
        self,
        request: httpx.Request,
        path: str,
        query: dict[str, list[str]],
    ) -> httpx.Response:
        state = self.state

        if path == "/actuator/health":
            return self._json_response(200, {"status": "UP"})

        if path.startswith("/api/audit"):
            _, err = self._require_auth(request, {"ADMIN"})
            if err is not None:
                return err
            return self._json_response(200, state.audit_logs)

        principal, err = self._require_auth(request)
        if err is not None or principal is None:
            return err  # type: ignore[return-value]
        username, roles = principal

        if path == "/api/auth/me":
            return self._json_response(200, {"username": username, "roles": roles})

        if path == "/api/reporting/reconciliation":
            as_of = query.get("asOf", [date.today().isoformat()])[0]
            return self._json_response(
                200,
                {
                    "asOf": as_of,
                    "healthy": True,
                    "trialBalanceBalanced": True,
                    "subledgerChecks": [
                        {
                            "label": "Inventory (Raw Materials)",
                            "accountCode": "1310",
                            "subledger": "1000.0000",
                            "glControl": "1000.0000",
                            "reconciled": True,
                        },
                        {
                            "label": "Accounts Payable",
                            "accountCode": "2100",
                            "subledger": "500.0000",
                            "glControl": "500.0000",
                            "reconciled": True,
                        },
                        {
                            "label": "Accounts Receivable",
                            "accountCode": "1200",
                            "subledger": "800.0000",
                            "glControl": "800.0000",
                            "reconciled": True,
                        },
                    ],
                    "clearingAccounts": [
                        {"accountCode": "2150", "name": "GR-IR Clearing", "balance": "0.0000", "cleared": True},
                        {"accountCode": "1320", "name": "Work-In-Process (WIP)", "balance": "0.0000", "cleared": True},
                    ],
                },
            )

        if path in ("/api/ledger/trial-balance", "/api/reporting/trial-balance"):
            total_dt = sum(Decimal(e["totalDebit"]) for e in state.journal_entries.values())
            total_ct = sum(Decimal(e["totalCredit"]) for e in state.journal_entries.values())
            return self._json_response(
                200,
                {
                    "lines": [
                        {
                            "accountCode": "1010",
                            "accountName": "Cash / Bank",
                            "debit": f"{total_dt:.4f}",
                            "credit": "0.0000",
                        },
                        {
                            "accountCode": "3100",
                            "accountName": "Share Capital",
                            "debit": "0.0000",
                            "credit": f"{total_ct:.4f}",
                        },
                    ],
                    "totalDebit": f"{total_dt:.4f}",
                    "totalCredit": f"{total_ct:.4f}",
                    "balanced": total_dt == total_ct,
                },
            )

        if path == "/api/masterdata/items":
            return self._json_response(200, list(state.items.values()))

        if path == "/api/masterdata/items/by-sku":
            sku = query.get("sku", [""])[0]
            for item in state.items.values():
                if item["sku"] == sku:
                    return self._json_response(200, item)
            return self._problem_response(404, "Not Found", f"Item not found for SKU: {sku}")

        m_item = re.fullmatch(r"/api/masterdata/items/(\d+)", path)
        if m_item:
            item_id = int(m_item.group(1))
            if item_id not in state.items:
                return self._problem_response(404, "Not Found", f"Item not found: {item_id}")
            return self._json_response(200, state.items[item_id])

        if path == "/api/masterdata/partners":
            return self._json_response(200, list(state.partners.values()))

        m_partner = re.fullmatch(r"/api/masterdata/partners/(\d+)", path)
        if m_partner:
            partner_id = int(m_partner.group(1))
            if partner_id not in state.partners:
                return self._problem_response(404, "Not Found", f"Partner not found: {partner_id}")
            return self._json_response(200, state.partners[partner_id])

        if path == "/api/masterdata/warehouses":
            return self._json_response(200, list(state.warehouses.values()))

        m_je = re.fullmatch(r"/api/ledger/journal-entries/(\d+)", path)
        if m_je:
            entry_no = int(m_je.group(1))
            if entry_no not in state.journal_entries:
                return self._problem_response(404, "Not Found", f"Journal entry not found: {entry_no}")
            return self._json_response(200, state.journal_entries[entry_no])

        if path == "/api/sales/sales-orders":
            return self._json_response(200, list(state.sales_orders.values()))

        m_so = re.fullmatch(r"/api/sales/sales-orders/(\d+)", path)
        if m_so:
            so_id = int(m_so.group(1))
            if so_id not in state.sales_orders:
                return self._problem_response(404, "Not Found", f"Sales order not found: {so_id}")
            return self._json_response(200, state.sales_orders[so_id])

        if path == "/api/purchasing/purchase-orders":
            return self._json_response(200, list(state.purchase_orders.values()))

        m_po = re.fullmatch(r"/api/purchasing/purchase-orders/(\d+)", path)
        if m_po:
            po_id = int(m_po.group(1))
            if po_id not in state.purchase_orders:
                return self._problem_response(404, "Not Found", f"Purchase order not found: {po_id}")
            return self._json_response(200, state.purchase_orders[po_id])

        m_onhand = re.fullmatch(r"/api/inventory/items/(\d+)/on-hand", path)
        if m_onhand:
            item_id = int(m_onhand.group(1))
            if item_id not in state.items:
                return self._problem_response(404, "Not Found", f"Item not found: {item_id}")
            itm = state.items[item_id]
            return self._json_response(
                200,
                {
                    "itemId": item_id,
                    "sku": itm["sku"],
                    "onHandQty": "100.000000",
                    "avgUnitCost": itm["standardCost"],
                    "totalValue": "1000.0000",
                },
            )

        return self._problem_response(404, "Not Found", f"No handler for GET {path}")

    def _handle_post(self, request: httpx.Request, path: str) -> httpx.Response:
        state = self.state

        if path == "/api/auth/login":
            body = self._parse_body(request)
            if not body or not body.get("username") or not body.get("password"):
                return self._problem_response(
                    400, "Bad Request", "username must not be blank; password must not be blank"
                )
            uname = str(body["username"])
            pwd = str(body["password"])
            matched = next(
                (acc for acc in ROLE_ACCOUNTS.values() if acc.username == uname and acc.password == pwd),
                None,
            )
            if matched is None:
                return self._problem_response(401, "Unauthorized", "Invalid username or password")
            token = f"jwt-{uname}-token"
            roles = list(matched.expected_roles)
            with state.lock:
                state.tokens[token] = (uname, roles)
            return self._json_response(
                200,
                {"accessToken": token, "username": uname, "roles": roles},
                extra_headers={"Set-Cookie": f"erp_refresh=refresh-{uname}; Path=/api/auth; HttpOnly; SameSite=Lax"},
            )

        if path == "/api/auth/logout":
            return httpx.Response(status_code=204)

        if path.startswith("/api/masterdata/"):
            _, err = self._require_auth(request, {"ADMIN"})
            if err is not None:
                return err
            body = self._parse_body(request)
            if body is None:
                return self._problem_response(400, "Bad Request", "Malformed or missing request body")

            if path == "/api/masterdata/items":
                sku = str(body.get("sku", "")).strip()
                name = str(body.get("name", "")).strip()
                item_type = body.get("itemType")
                uom = str(body.get("uom", "")).strip()
                if not sku or not name or not item_type or not uom:
                    return self._problem_response(400, "Bad Request", "sku, name, itemType, uom are required")
                with state.lock:
                    if any(i["sku"] == sku for i in state.items.values()):
                        return self._problem_response(409, "Conflict", f"Duplicate item SKU: {sku}")
                    new_id = max(state.items.keys(), default=0) + 1
                    item_obj = {
                        "id": new_id,
                        "sku": sku,
                        "name": name,
                        "itemType": item_type,
                        "uom": uom,
                        "stocked": bool(body.get("stocked", True)),
                        "standardCost": f"{Decimal(str(body.get('standardCost', '0'))):.6f}",
                        "reorderPoint": f"{Decimal(str(body.get('reorderPoint', '0'))):.6f}",
                        "reorderQty": f"{Decimal(str(body.get('reorderQty', '0'))):.6f}",
                    }
                    state.items[new_id] = item_obj
                return self._json_response(201, item_obj)

            if path == "/api/masterdata/partners":
                code = str(body.get("code", "")).strip()
                name = str(body.get("name", "")).strip()
                if not code or not name:
                    return self._problem_response(
                        400, "Bad Request", "code must not be blank; name must not be blank"
                    )
                with state.lock:
                    if any(p["code"] == code for p in state.partners.values()):
                        return self._problem_response(409, "Conflict", f"Duplicate partner code: {code}")
                    new_id = max(state.partners.keys(), default=0) + 1
                    partner_obj = {
                        "id": new_id,
                        "code": code,
                        "name": name,
                        "vendor": bool(body.get("vendor", False)),
                        "customer": bool(body.get("customer", False)),
                        "taxId": body.get("taxId"),
                        "paymentTermsDays": int(body.get("paymentTermsDays", 30)),
                        "apAccountCode": body.get("apAccountCode"),
                        "arAccountCode": body.get("arAccountCode"),
                        "active": True,
                    }
                    state.partners[new_id] = partner_obj
                return self._json_response(201, partner_obj)

            if path == "/api/masterdata/warehouses":
                code = str(body.get("code", "")).strip()
                name = str(body.get("name", "")).strip()
                if not code or not name:
                    return self._problem_response(400, "Bad Request", "code and name are required")
                with state.lock:
                    new_id = max(state.warehouses.keys(), default=0) + 1
                    wh_obj = {"id": new_id, "code": code, "name": name, "active": True}
                    state.warehouses[new_id] = wh_obj
                return self._json_response(201, wh_obj)

        if path == "/api/ledger/journal-entries":
            _, err = self._require_auth(request, {"ACCOUNTANT"})
            if err is not None:
                return err
            body = self._parse_body(request)
            if not body or not body.get("postingDate") or not body.get("lines"):
                return self._problem_response(
                    400, "Bad Request", "postingDate must not be null; lines must not be empty"
                )
            lines = body["lines"]
            if not isinstance(lines, list) or len(lines) < 2:
                return self._problem_response(400, "Bad Request", "journal entry requires at least two lines")
            total_debit = Decimal("0.0000")
            total_credit = Decimal("0.0000")
            detail_lines = []
            for line in lines:
                acc_code = str(line.get("accountCode", ""))
                if acc_code not in state.accounts:
                    return self._problem_response(400, "Bad Request", f"Account not found: {acc_code}")
                try:
                    dt = Decimal(str(line.get("debit", "0")))
                    ct = Decimal(str(line.get("credit", "0")))
                except InvalidOperation:
                    return self._problem_response(400, "Bad Request", "Invalid decimal amount")
                if dt < 0 or ct < 0 or (dt > 0 and ct > 0) or (dt == 0 and ct == 0):
                    return self._problem_response(
                        400, "Bad Request", "Line must have strictly positive debit XOR credit"
                    )
                total_debit += dt
                total_credit += ct
                detail_lines.append(
                    {
                        "accountCode": acc_code,
                        "accountName": state.accounts[acc_code],
                        "debit": f"{dt:.4f}",
                        "credit": f"{ct:.4f}",
                        "memo": line.get("memo"),
                        "partnerId": line.get("partnerId"),
                    }
                )
            if total_debit != total_credit:
                return self._problem_response(
                    422,
                    "Unprocessable Entity",
                    f"Unbalanced journal entry: debit={total_debit:.4f}, credit={total_credit:.4f}",
                )
            with state.lock:
                entry_no = max(state.journal_entries.keys(), default=0) + 1
                je_detail = {
                    "id": entry_no,
                    "entryNo": entry_no,
                    "status": "POSTED",
                    "postingDate": str(body["postingDate"]),
                    "currencyCode": str(body.get("currencyCode") or "TWD"),
                    "memo": body.get("memo"),
                    "sourceDocType": body.get("sourceDocType"),
                    "sourceDocId": body.get("sourceDocId"),
                    "reversesEntryNo": None,
                    "reversedByEntryNo": None,
                    "totalDebit": f"{total_debit:.4f}",
                    "totalCredit": f"{total_credit:.4f}",
                    "lines": detail_lines,
                }
                state.journal_entries[entry_no] = je_detail
            return self._json_response(
                201,
                {
                    "id": entry_no,
                    "entryNo": entry_no,
                    "status": "POSTED",
                    "postingDate": je_detail["postingDate"],
                    "currencyCode": je_detail["currencyCode"],
                    "totalDebit": je_detail["totalDebit"],
                    "totalCredit": je_detail["totalCredit"],
                },
            )

        if path.startswith("/api/sales/sales-orders"):
            _, err = self._require_auth(request, {"SALES"})
            if err is not None:
                return err
            if path == "/api/sales/sales-orders":
                body = self._parse_body(request)
                if not body or not body.get("partnerId") or not body.get("orderDate") or not body.get("lines"):
                    return self._problem_response(
                        400,
                        "Bad Request",
                        "partnerId must not be null; orderDate must not be null; lines must not be empty",
                    )
                partner_id = int(body["partnerId"])
                if partner_id not in state.partners:
                    return self._problem_response(404, "Not Found", f"Partner not found: {partner_id}")
                with state.lock:
                    so_id = max(state.sales_orders.keys(), default=0) + 1
                    so_lines = []
                    for idx, line in enumerate(body["lines"], start=1):
                        so_lines.append(
                            {
                                "id": so_id * 100 + idx,
                                "lineNo": idx,
                                "itemId": int(line["itemId"]),
                                "qtyOrdered": f"{Decimal(str(line['qtyOrdered'])):.6f}",
                                "qtyShipped": "0.000000",
                                "qtyInvoiced": "0.000000",
                                "unitPrice": f"{Decimal(str(line['unitPrice'])):.4f}",
                            }
                        )
                    so_obj = {
                        "id": so_id,
                        "soNumber": f"SO-{so_id:06d}",
                        "partnerId": partner_id,
                        "orderDate": str(body["orderDate"]),
                        "status": "DRAFT",
                        "lines": so_lines,
                    }
                    state.sales_orders[so_id] = so_obj
                return self._json_response(201, so_obj)

            m_confirm = re.fullmatch(r"/api/sales/sales-orders/(\d+)/confirm", path)
            if m_confirm:
                so_id = int(m_confirm.group(1))
                if so_id not in state.sales_orders:
                    return self._problem_response(404, "Not Found", f"Sales order not found: {so_id}")
                so_obj = state.sales_orders[so_id]
                if so_obj["status"] != "DRAFT":
                    return self._problem_response(409, "Conflict", "Sales order is already confirmed")
                so_obj["status"] = "CONFIRMED"
                return self._json_response(200, so_obj)

        if path.startswith("/api/purchasing/purchase-orders"):
            _, err = self._require_auth(request, {"WAREHOUSE"})
            if err is not None:
                return err
            if path == "/api/purchasing/purchase-orders":
                body = self._parse_body(request)
                if not body or not body.get("partnerId") or not body.get("orderDate") or not body.get("lines"):
                    return self._problem_response(
                        400,
                        "Bad Request",
                        "partnerId must not be null; orderDate must not be null; lines must not be empty",
                    )
                partner_id = int(body["partnerId"])
                if partner_id not in state.partners:
                    return self._problem_response(404, "Not Found", f"Partner not found: {partner_id}")
                with state.lock:
                    po_id = max(state.purchase_orders.keys(), default=0) + 1
                    po_lines = []
                    for idx, line in enumerate(body["lines"], start=1):
                        po_lines.append(
                            {
                                "id": po_id * 100 + idx,
                                "lineNo": idx,
                                "itemId": int(line["itemId"]),
                                "qtyOrdered": f"{Decimal(str(line['qtyOrdered'])):.6f}",
                                "qtyReceived": "0.000000",
                                "qtyBilled": "0.000000",
                                "unitPrice": f"{Decimal(str(line['unitPrice'])):.4f}",
                            }
                        )
                    po_obj = {
                        "id": po_id,
                        "poNumber": f"PO-{po_id:06d}",
                        "partnerId": partner_id,
                        "orderDate": str(body["orderDate"]),
                        "status": "DRAFT",
                        "lines": po_lines,
                    }
                    state.purchase_orders[po_id] = po_obj
                return self._json_response(201, po_obj)

        return self._problem_response(404, "Not Found", f"No handler for POST {path}")
