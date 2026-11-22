"""
Page Object for the Main Dashboard & Reconciliation Hero Check (`/`).

Corresponds to the frontend presentation of `GET /api/reporting/reconciliation`
(TC-UI-AK-01 / TC-API-AK-01), verifying double-entry balance and subledger reconciliation.
"""

from __future__ import annotations

from typing import Optional

from playwright.sync_api import Locator, expect

from tests.pages.base_page import BaseErpPage


class DashboardPage(BaseErpPage):
    """Page Object representing `/` (DashboardPage.tsx + ReconciliationHero.tsx)."""

    @property
    def reconciliation_hero(self) -> Locator:
        """Returns the Reconciliation Hero section container on the Dashboard."""
        return self.page.locator('[data-onboarding="reconciliation-hero"]')

    def open(self) -> DashboardPage:
        """Navigates to `/` and waits for the Dashboard heading to render."""
        self.goto("/")
        expect(self.page.get_by_role("heading", name="Dashboard")).to_be_visible()
        return self

    def expect_signed_in_identity(self, username: str, expected_role_badge: Optional[str] = None) -> None:
        """Verifies the 'Signed in as <username>' banner and optional role badge."""
        expect(self.page.get_by_text("Signed in as")).to_be_visible()
        expect(self.page.get_by_text(username, exact=True).first).to_be_visible()
        if expected_role_badge:
            expect(self.page.locator(".mantine-Badge-root").filter(has_text=expected_role_badge).first).to_be_visible()

    def expect_reconciliation_healthy(self) -> None:
        """
        Asserts that the Reconciliation Hero Check displays 'Books reconcile'
        and the green 'Trial balance balanced' badge.
        """
        hero = self.reconciliation_hero
        expect(hero).to_be_visible()
        expect(hero.get_by_role("heading", name="Books reconcile")).to_be_visible(timeout=10_000)
        expect(hero.get_by_text("Trial balance balanced", exact=True)).to_be_visible()

    def expect_subledger_row_reconciled(self, account_code: str) -> Locator:
        """
        Verifies that the subledger row for `account_code` (e.g. '1200', '2100', '1310')
        is present in the Reconciliation Hero table and carries the 'Reconciled' status icon.
        """
        row = self.reconciliation_hero.locator("tbody tr").filter(has_text=account_code).first
        expect(row).to_be_visible()
        reconciled_icon = row.get_by_role("img", name="Reconciled", exact=True)
        expect(reconciled_icon).to_be_visible()
        return row

    def expect_all_subledgers_reconciled(self) -> int:
        """
        Verifies that every subledger row rendered in the Reconciliation Hero table
        has a 'Reconciled' indicator and returns the number of verified rows.
        """
        rows = self.reconciliation_hero.locator("tbody tr")
        count = rows.count()
        assert count >= 3, f"Expected at least 3 subledger reconciliation rows, found {count}"
        for idx in range(count):
            row = rows.nth(idx)
            expect(row.get_by_role("img", name="Reconciled", exact=True)).to_be_visible()
        return count

    def expect_all_clearing_accounts_cleared(self) -> int:
        """
        Verifies that all transitional clearing account cards (GR/IR, WIP, Deferred COGS)
        in the Reconciliation Hero section show the 'Cleared' check icon.
        """
        cleared_icons = self.reconciliation_hero.get_by_role("img", name="Cleared", exact=True)
        expect(cleared_icons.first).to_be_visible()
        count = cleared_icons.count()
        assert count >= 2, f"Expected at least 2 cleared transitional accounts, found {count}"
        return count

