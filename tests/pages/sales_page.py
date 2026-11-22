"""
Page Object for the Sales (Order-to-Cash) view (`/sales`).

Encapsulates UI interactions for Sales Orders (`SalesOrdersPanel.tsx`),
Deliveries, Invoices, and AR Aging — reusable across both team members' suites.
"""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from tests.pages.base_page import BaseErpPage


class SalesPage(BaseErpPage):
    """Page Object representing `/sales` (SalesPage.tsx & SalesOrdersPanel.tsx)."""

    def open(self) -> SalesPage:
        """Navigates to `/sales` and waits for the Sales page header."""
        self.goto("/sales")
        expect(self.page.get_by_role("heading", name="Sales")).to_be_visible()
        return self

    def open_new_sales_order_modal(self) -> Locator:
        """Clicks 'New sales order' and returns the opened Mantine Modal locator."""
        new_btn = self.page.get_by_role("button", name="New sales order").first
        expect(new_btn).to_be_visible()
        new_btn.click()
        return self.get_open_modal("New sales order")

    def submit_empty_sales_order_and_expect_validation_error(self) -> None:
        """
        Opens the 'New sales order' modal, clicks 'Create' without selecting a customer
        or line items, and verifies that the validation error 'Pick a customer' is shown.
        """
        modal = self.open_new_sales_order_modal()
        modal.get_by_role("button", name="Create", exact=True).click()
        expect(modal.get_by_text("Pick a customer")).to_be_visible()
        expect(modal).to_be_visible()

