"""
Page Object for the Authentication / Sign-In view (`/login`).

Provides reusable login workflows (form submission, quick demo role buttons,
read-only guest entry, and invalid credential error verification) for all team members.
"""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from tests.config import ROLE_ACCOUNTS, ErpRole
from tests.pages.base_page import BaseErpPage


class LoginPage(BaseErpPage):
    """Page Object representing `/login` (LoginPage.tsx)."""

    @property
    def username_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Username")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_role("textbox", name="Password")

    @property
    def sign_in_button(self) -> Locator:
        return self.page.get_by_role("button", name="Sign in", exact=True)

    @property
    def guest_entry_button(self) -> Locator:
        return self.page.get_by_role("button", name="Browse as guest (read-only)", exact=True)

    def open(self) -> LoginPage:
        """Opens `/login` and waits until the login card is rendered."""
        self.init_deterministic_ui_preferences()
        self.goto("/login")
        expect(self.sign_in_button).to_be_visible()
        return self

    def login_with_credentials(self, username: str, password: str) -> None:
        """Fills the Username and Password inputs and submits the sign-in form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.sign_in_button.click()

    def login_as_role(self, role: ErpRole) -> None:
        """Authenticates via the UI using the credentials configured for `role`."""
        self.open()
        if role == ErpRole.GUEST:
            self.login_as_guest()
            return
        account = ROLE_ACCOUNTS[role]
        self.login_with_credentials(account.username, account.password)
        self.expect_pathname("/")

    def login_via_quick_demo_button(self, role_username: str) -> None:
        """Clicks one of the quick demo role buttons ('admin', 'accountant', 'sales', etc.)."""
        self.open()
        quick_btn = self.page.get_by_role("button", name=role_username, exact=True)
        expect(quick_btn).to_be_visible()
        quick_btn.click()
        self.expect_pathname("/")

    def login_as_guest(self) -> None:
        """Clicks 'Browse as guest (read-only)' and waits for redirect to Dashboard."""
        expect(self.guest_entry_button).to_be_visible()
        self.guest_entry_button.click()
        self.expect_pathname("/")

    def expect_invalid_credentials_error(self) -> None:
        """Asserts that the red Alert 'Invalid username or password' is displayed."""
        alert = self.page.get_by_role("alert").filter(has_text="Invalid username or password")
        expect(alert).to_be_visible()
