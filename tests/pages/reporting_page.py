"""Page Object for trial-balance presentation; distinct from the Dashboard Hero."""

from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from urllib.parse import urlsplit

from playwright.sync_api import expect

from tests.pages.base_page import BaseErpPage


def displayed_amount(raw: str | int) -> str:
    """The frontend truncates to two decimals; Decimal avoids float rounding drift."""
    amount = Decimal(str(raw)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    return f"{amount:,.2f}"


class ReportingPage(BaseErpPage):
    def expect_trial_balance_matches_api(self) -> None:
        with self.page.expect_response(
            lambda response: urlsplit(response.url).path == "/api/reporting/trial-balance"
            and response.request.method == "GET",
        ) as response_info:
            self.goto("/reporting?tab=trial-balance")
        response = response_info.value
        assert response.status == 200
        body = response.json()
        assert isinstance(body.get("lines"), list) and body["lines"], "Trial balance requires seeded accounts"
        panel = self.page.get_by_role("tabpanel", name="Trial balance", exact=True)
        expect(panel).to_be_visible()
        expect(panel.get_by_text("Balanced" if body["balanced"] else "Unbalanced", exact=True)).to_be_visible()
        totals = panel.locator("tfoot tr th")
        expect(totals.nth(1)).to_have_text(displayed_amount(body["totalDebit"]))
        expect(totals.nth(2)).to_have_text(displayed_amount(body["totalCredit"]))
        first = body["lines"][0]
        row = panel.locator("tbody tr").filter(
            has=self.page.get_by_role("cell", name=str(first["code"]), exact=True)
        )
        expect(row).to_have_count(1)
        cells = row.locator("td")
        expect(cells.nth(1)).to_have_text(first.get("name") or "")
        expect(cells.nth(3)).to_have_text(displayed_amount(first["debit"]))
        expect(cells.nth(4)).to_have_text(displayed_amount(first["credit"]))
