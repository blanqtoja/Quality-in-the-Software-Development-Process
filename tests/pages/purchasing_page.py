"""Page Object for purchase-order validation, shared with the existing Python POM."""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from tests.pages.base_page import BaseErpPage


class PurchasingPage(BaseErpPage):
    def open(self) -> PurchasingPage:
        self.goto("/purchasing?tab=orders")
        expect(self.page.get_by_role("heading", name="Purchasing", exact=True)).to_be_visible()
        return self

    def open_order_with_vendor(self, vendor_code: str) -> Locator:
        self.page.get_by_role("button", name="New purchase order", exact=True).first.click()
        modal = self.get_open_modal("New purchase order")
        picker = modal.get_by_role("combobox", name="Vendor")
        expect(picker).to_be_enabled()
        self.select_searchable_combobox_option(picker, vendor_code)
        return modal

    def submit_incomplete_order(self, modal: Locator) -> None:
        modal.get_by_role("button", name="Create", exact=True).click()
        self.expect_toast_notification("Add at least one complete line")
        expect(modal).to_be_visible()
