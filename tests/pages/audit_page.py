"""
Page Object for the Audit Trail view (`/audit`) and RBAC 403 Forbidden guard (`ForbiddenPage.tsx`).

Corresponds to the frontend presentation of `GET /api/audit` RBAC access control
(TC-UI-AK-02 / TC-API-AK-04).
"""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BaseErpPage


class AuditPage(BaseErpPage):
    """Page Object representing `/audit` and its `<RequireRole role="ADMIN">` guard."""

    def open_directly(self) -> AuditPage:
        """Navigates directly to `/audit` via the browser address bar."""
        self.goto("/audit")
        return self

    def expect_forbidden_403_view(self) -> None:
        """
        Asserts that the 403 Forbidden screen (`ForbiddenPage.tsx`) is rendered
        when a non-ADMIN user attempts to access `/audit`.
        """
        expect(self.page.get_by_role("heading", name="403", exact=True)).to_be_visible()
        expect(
            self.page.get_by_text("You don't have the role required for this action.")
        ).to_be_visible()
        expect(
            self.page.get_by_role("button", name="Back to dashboard", exact=True)
        ).to_be_visible()

    def click_back_to_dashboard(self) -> None:
        """Clicks the 'Back to dashboard' button on the 403 page and verifies redirect to `/`."""
        btn = self.page.get_by_role("button", name="Back to dashboard", exact=True)
        expect(btn).to_be_visible()
        btn.click()
        self.expect_pathname("/")

    def expect_audit_trail_accessible(self) -> None:
        """Asserts that an authorized ADMIN user sees the Audit Trail heading."""
        expect(self.page.get_by_role("heading", name="Audit Trail")).to_be_visible()

