"""
Page Object for the General Ledger view (`/ledger`).

Encapsulates UI interactions for Manual Journal Entries (`ManualEntryPanel.tsx`),
Reversals (`ReversalPanel.tsx`), and Fiscal Periods (`FiscalPeriodsPanel.tsx`).
Directly supports TC-UI-AK-04 (corresponding to TC-API-AK-06 & TC-API-AK-07).
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, expect

from tests.pages.base_page import BaseErpPage


class LedgerPage(BaseErpPage):
    """Page Object representing `/ledger` (LedgerPage.tsx & ManualEntryPanel.tsx)."""

    def open(self) -> LedgerPage:
        """Navigates to `/ledger` and waits for the Ledger page header."""
        self.goto("/ledger")
        expect(self.page.get_by_role("heading", name="Ledger")).to_be_visible()
        return self

    def open_manual_entry_tab(self) -> LedgerPage:
        self.select_tab("Manual entry")
        return self

    def open_reversal_tab(self) -> LedgerPage:
        self.select_tab("Reversal")
        return self

    def open_periods_tab(self) -> LedgerPage:
        self.select_tab("Fiscal periods")
        return self

    @property
    def post_entry_button(self) -> Locator:
        """Returns the 'Post entry' button on the Manual entry panel."""
        return self.page.get_by_role("button", name="Post entry", exact=True)

    def set_header_memo(self, memo: str) -> None:
        """Fills the top-level journal entry Memo field."""
        self.page.get_by_label("Memo").first.fill(memo)

    def fill_journal_line(
        self,
        row_index: int,
        *,
        account_code: str,
        debit: str = "",
        credit: str = "",
        line_memo: str = "",
    ) -> None:
        """
        Populates row `row_index` (0-based) of the Manual Journal Entry lines table:
        selects the GL account from the searchable combobox and fills Debit, Credit, and Memo.
        """
        row = self.page.locator("tbody tr").nth(row_index)
        expect(row).to_be_visible()

        cells = row.locator("td")
        account_input = cells.nth(0).locator("input:not([type='hidden'])")
        debit_input = cells.nth(1).locator("input")
        credit_input = cells.nth(2).locator("input")
        memo_input = cells.nth(3).locator("input")

        self.select_searchable_combobox_option(account_input, account_code)
        debit_input.fill(debit)
        credit_input.fill(credit)
        if line_memo:
            memo_input.fill(line_memo)

    def expect_unbalanced_state(self) -> None:
        """
        Asserts that the UI flags the current journal entry as 'Unbalanced'
        and disables the 'Post entry' button (preventing asymmetric double-entry post).
        """
        badge = self.page.locator(".mantine-Badge-root").filter(has_text=re.compile(r"^Unbalanced$", re.I))
        expect(badge).to_be_visible()
        expect(self.post_entry_button).to_be_disabled()

    def expect_balanced_state(self) -> None:
        """
        Asserts that the UI displays the teal 'Balanced' badge and enables
        the 'Post entry' button once total debits equal total credits (> 0).
        """
        badge = self.page.locator(".mantine-Badge-root").filter(has_text=re.compile(r"^Balanced$", re.I))
        expect(badge).to_be_visible()
        expect(self.post_entry_button).to_be_enabled()

    def submit_manual_entry_and_expect_posted(self) -> str:
        """
        Clicks 'Post entry' and verifies the toast notification 'Journal entry #<no> posted'.
        Returns the notification text.
        """
        expect(self.post_entry_button).to_be_enabled()
        self.post_entry_button.click()
        toast = self.expect_toast_notification(re.compile(r"Journal entry #\d+ posted", re.I))
        return toast.inner_text()
