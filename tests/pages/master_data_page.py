"""
Page Object for the Master Data view (`/masterdata`).

Encapsulates UI interactions across all Master Data tabs (`Items`, `Partners`,
`Warehouses`, `Locations`), providing reusable creation and table verification
methods for both Aleksander Kazmierczak (TC-UI-AK-03) and Lukasz Murza.
"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Locator, expect

from tests.pages.base_page import BaseErpPage


class MasterDataPage(BaseErpPage):
    """Page Object representing `/masterdata` (MasterDataPage.tsx)."""

    def open(self) -> MasterDataPage:
        """Navigates to `/masterdata` and waits for the Master Data header."""
        self.goto("/masterdata")
        expect(self.page.get_by_role("heading", name="Master Data")).to_be_visible()
        return self

    def open_items_tab(self) -> MasterDataPage:
        self.select_tab("Items")
        return self

    def open_partners_tab(self) -> MasterDataPage:
        self.select_tab("Partners")
        return self

    def open_warehouses_tab(self) -> MasterDataPage:
        self.select_tab("Warehouses")
        return self

    def open_locations_tab(self) -> MasterDataPage:
        self.select_tab("Locations")
        return self

    # ------------------------------------------------------------------
    # Partners Tab Helpers (TC-UI-AK-03 / POST /api/masterdata/partners)
    # ------------------------------------------------------------------

    def create_partner_via_modal(
        self,
        *,
        code: str,
        name: str,
        vendor: bool = True,
        customer: bool = True,
        tax_id: str = "PL5260001234",
        payment_terms_days: int = 45,
        ap_account_code: str = "2100",
        ar_account_code: str = "1200",
    ) -> None:
        """
        Opens the 'New partner' modal, populates all form fields, submits the form,
        and verifies the success toast notification.
        """
        self.open_partners_tab()
        new_btn = self.page.get_by_role("button", name="New partner").first
        expect(new_btn).to_be_visible()
        new_btn.click()

        modal = self.get_open_modal("New partner")
        modal.get_by_label("Code").fill(code)
        modal.get_by_label("Name").fill(name)

        self.set_mantine_switch(modal, "Vendor", vendor)
        self.set_mantine_switch(modal, "Customer", customer)

        modal.get_by_label("Tax ID").fill(tax_id)
        terms_input = modal.get_by_label("Payment terms (days)")
        terms_input.fill(str(payment_terms_days))
        modal.get_by_label("AP account (override)").fill(ap_account_code)
        modal.get_by_label("AR account (override)").fill(ar_account_code)

        create_btn = modal.get_by_role("button", name="Create", exact=True)
        expect(create_btn).to_be_enabled()
        create_btn.click()

        self.expect_toast_notification(f"Partner {code} created")
        expect(modal).to_be_hidden()

    def find_table_row_Across_pages(self, unique_key_text: str) -> Locator:
        """
        Locates a `<tr>` row containing `unique_key_text` in the active DataTable,
        automatically advancing to the last pagination page if the table exceeds 25 rows.
        """
        row = self.page.locator("tbody tr").filter(has_text=unique_key_text)
        if row.count() > 0 and row.first.is_visible():
            return row.first

        pagination_buttons = self.page.locator(".mantine-Pagination-control")
        if pagination_buttons.count() > 2:
            # Click the second-to-last control (the highest page number before 'next')
            pagination_buttons.nth(pagination_buttons.count() - 2).click()

        expect(row.first).to_be_visible()
        return row.first

    def expect_partner_in_table(
        self,
        *,
        code: str,
        name: str,
        vendor: bool = True,
        customer: bool = True,
        payment_terms_days: Optional[int] = None,
    ) -> Locator:
        """Asserts that the partner with `code` is rendered in the Partners DataTable."""
        row = self.find_table_row_Across_pages(code)
        expect(row).to_contain_text(name)
        if vendor:
            expect(row).to_contain_text("Vendor")
        if customer:
            expect(row).to_contain_text("Customer")
        if payment_terms_days is not None:
            expect(row).to_contain_text(str(payment_terms_days))
        return row

    def expect_partner_read_only(self, *, code: str, name: str) -> None:
        """Check an actual partner row as well as the absence of write controls."""
        row = self.find_table_row_Across_pages(code)
        expect(row.get_by_role("cell", name=code, exact=True)).to_be_visible()
        expect(row.get_by_role("cell", name=name, exact=True)).to_be_visible()
        expect(self.page.get_by_role("button", name="New partner", exact=True)).to_have_count(0)
        expect(self.page.get_by_role("dialog")).to_have_count(0)

    # ------------------------------------------------------------------
    # Items Tab Helpers (Reusable for Item creation & lookup tests)
    # ------------------------------------------------------------------

    def create_item_via_modal(
        self,
        *,
        sku: str,
        name: str,
        uom: str = "PCS",
        standard_cost: str = "25.50",
        stocked: bool = True,
    ) -> None:
        """Opens the 'New item' modal, fills item details, submits, and verifies toast."""
        self.open_items_tab()
        new_btn = self.page.get_by_role("button", name="New item").first
        expect(new_btn).to_be_visible()
        new_btn.click()

        modal = self.get_open_modal("New item")
        modal.get_by_label("SKU").fill(sku)
        modal.get_by_label("Name").fill(name)
        modal.get_by_label("Unit of measure").fill(uom)
        modal.get_by_label("Standard cost").fill(standard_cost)
        self.set_mantine_switch(modal, "Stocked", stocked)

        modal.get_by_role("button", name="Create", exact=True).click()
        self.expect_toast_notification(f"Item {sku} created")
        expect(modal).to_be_hidden()

    def expect_item_in_table(self, *, sku: str, name: Optional[str] = None) -> Locator:
        """Asserts that the item with `sku` is displayed in the Items DataTable."""
        self.open_items_tab()
        row = self.find_table_row_Across_pages(sku)
        if name:
            expect(row).to_contain_text(name)
        return row

    # ------------------------------------------------------------------
    # Warehouses Tab Helpers (Reusable for Second Team Member)
    # ------------------------------------------------------------------

    def create_warehouse_via_modal(self, *, code: str, name: str) -> None:
        """Opens the 'New warehouse' modal, fills code & name, submits, and verifies toast."""
        self.open_warehouses_tab()
        new_btn = self.page.get_by_role("button", name="New warehouse").first
        expect(new_btn).to_be_visible()
        new_btn.click()

        modal = self.get_open_modal("New warehouse")
        modal.get_by_label("Code").fill(code)
        modal.get_by_label("Name").fill(name)
        modal.get_by_role("button", name="Create", exact=True).click()
        self.expect_toast_notification(f"Warehouse {code} created")
        expect(modal).to_be_hidden()

