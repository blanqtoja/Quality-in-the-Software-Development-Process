"""
Page Object Model (POM) package for Manufacturing ERP Frontend E2E Testing.

Exports all Page Objects so both team members (Aleksander Kazmierczak & Lukasz Murza)
can write clean, declarative, DRY frontend tests without duplicating DOM locators.
"""

from tests.pages.audit_page import AuditPage
from tests.pages.base_page import BaseErpPage
from tests.pages.dashboard_page import DashboardPage
from tests.pages.ledger_page import LedgerPage
from tests.pages.login_page import LoginPage
from tests.pages.master_data_page import MasterDataPage
from tests.pages.sales_page import SalesPage

__all__ = [
    "AuditPage",
    "BaseErpPage",
    "DashboardPage",
    "LedgerPage",
    "LoginPage",
    "MasterDataPage",
    "SalesPage",
]

