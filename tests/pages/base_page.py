"""
Base Page Object Model (BaseErpPage) following DRY and Single Responsibility Principles.

Encapsulates shared Playwright browser interactions, Mantine v9 UI component helpers
(AppShell navigation, Tabs, Modals, searchable Selects, Switches, and Toast Notifications),
and session initialization (pinning English locale and dismissing onboarding spotlights).
"""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Iterator, Pattern
from urllib.parse import urlsplit

from playwright.sync_api import Locator, Page, Request, expect


class BaseErpPage:
    """Base Page Object shared across all ERP frontend views."""

    def __init__(self, page: Page, frontend_base_url: str) -> None:
        self.page = page
        self.frontend_base_url = frontend_base_url.rstrip("/")

    def init_deterministic_ui_preferences(self) -> None:
        """
        Pins the SPA locale to English ('en') and marks the onboarding spotlight tour
        as completed before page scripts execute so automated interactions are deterministic.
        """
        self.page.add_init_script(
            """
            window.localStorage.setItem('erp.locale', 'en');
            window.localStorage.setItem(
                'erp.onboarding',
                JSON.stringify({ completed: true, currentStep: 99 })
            );
            """
        )

    def goto(self, path: str = "/") -> None:
        """Navigates to a path relative to the frontend base URL."""
        normalized = path if path.startswith("/") else f"/{path}"
        self.page.goto(f"{self.frontend_base_url}{normalized}", wait_until="domcontentloaded")

    @property
    def current_pathname(self) -> str:
        """Returns the current URL path component (e.g., '/masterdata')."""
        return urlsplit(self.page.url).path

    def expect_pathname(self, expected_path: str, timeout: float = 10_000) -> None:
        """Asserts that the browser URL path transitions to `expected_path`."""
        escaped = re.escape(expected_path)
        expect(self.page).to_have_url(re.compile(rf".*{escaped}(\?.*)?$"), timeout=timeout)

    @property
    def sidebar(self) -> Locator:
        """Returns the Mantine AppShell sidebar navigation container."""
        return self.page.locator(".mantine-AppShell-navbar")

    def navigate_via_sidebar(self, link_label: str) -> None:
        """Clicks a module link in the left sidebar navigation."""
        link = self.sidebar.get_by_role("link", name=link_label, exact=True)
        expect(link).to_be_visible()
        link.click()

    def is_sidebar_link_visible(self, link_label: str) -> bool:
        """Returns True if the given sidebar module link is rendered and visible."""
        link = self.sidebar.get_by_role("link", name=link_label, exact=True)
        return link.is_visible()

    def expect_sidebar_link_hidden(self, link_label: str) -> None:
        """Asserts that a restricted module link is not visible in the sidebar (RBAC check)."""
        link = self.sidebar.get_by_role("link", name=link_label, exact=True)
        expect(link).to_be_hidden()

    def select_tab(self, tab_label: str) -> None:
        """Switches to a Mantine tab by its accessible tab name."""
        tab = self.page.get_by_role("tab", name=tab_label, exact=True)
        expect(tab).to_be_visible()
        tab.click()
        expect(tab).to_have_attribute("aria-selected", "true")

    def get_open_modal(self, title_text: str | Pattern[str] | None = None) -> Locator:
        """Returns the currently open Mantine Modal dialog locator."""
        dialog = self.page.get_by_role("dialog")
        if title_text is not None:
            dialog = self.page.get_by_role("dialog", name=title_text)
        expect(dialog).to_be_visible()
        return dialog

    def select_searchable_combobox_option(
        self,
        input_locator: Locator,
        search_prefix: str,
        option_pattern: str | Pattern[str] | None = None,
    ) -> None:
        """
        Selects an item from a Mantine v9 searchable <Select> combobox.
        Skips re-clicking if the input already holds the target `search_prefix`
        (preventing Mantine's default allowDeselect toggle).
        """
        expect(input_locator).to_be_visible()
        current_val = input_locator.input_value().strip()
        if current_val.lower().startswith(search_prefix.lower()):
            return
        input_locator.click()
        input_locator.fill(search_prefix)
        target_pattern = option_pattern or re.compile(rf"^{re.escape(search_prefix)}\b", re.IGNORECASE)
        option = self.page.get_by_role("option", name=target_pattern).first
        expect(option).to_be_visible()
        option.click()

    def set_mantine_switch(self, container: Locator, label_text: str, checked: bool) -> None:
        """Sets a Mantine <Switch> state inside `container` by its visible label."""
        checkbox = container.get_by_label(label_text, exact=True)
        if checkbox.is_checked() != checked:
            # Mantine visually hides the raw checkbox input and styles the sibling track/label
            container.locator(".mantine-Switch-root").filter(has_text=label_text).click()
        expect(checkbox).to_be_checked(checked=checked)

    def expect_toast_notification(
        self,
        expected_text: str | Pattern[str],
        timeout: float = 10_000,
    ) -> Locator:
        """Asserts that a Mantine toast notification matching `expected_text` is visible."""
        notification = (
            self.page.locator(".mantine-Notification-root")
            .filter(has_text=expected_text)
            .first
        )
        expect(notification).to_be_visible(timeout=timeout)
        return notification

    @contextmanager
    def record_post_requests(self, path_prefix: str) -> Iterator[list[Request]]:
        """Observe writes without intercepting responses or replacing the backend."""
        requests: list[Request] = []

        def record(request: Request) -> None:
            if request.method == "POST" and urlsplit(request.url).path.startswith(path_prefix):
                requests.append(request)

        self.page.on("request", record)
        try:
            yield requests
        finally:
            self.page.remove_listener("request", record)
