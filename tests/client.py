"""
HTTP REST API client for the Manufacturing ERP system (SRP and DRY).

Encapsulates HTTPX communication, JWT authentication (POST /api/auth/login),
per-role Bearer token caching, and request header management.
Shared across all team members' test suites.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from tests.config import ROLE_ACCOUNTS, ApiSettings, ErpRole
from tests.models import TokenResponseModel


class ErpApiClient:
    """Shared REST API client with built-in RBAC role authentication and JWT caching."""

    def __init__(
        self,
        settings: ApiSettings,
        default_role: Optional[ErpRole] = None,
        token_cache: Optional[dict[ErpRole, str]] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.settings = settings
        self.default_role = default_role
        self._token_cache: dict[ErpRole, str] = token_cache if token_cache is not None else {}
        self._transport = transport
        client_kwargs: dict[str, Any] = {
            "base_url": settings.base_url,
            "timeout": settings.timeout_seconds,
            "headers": {"Accept": "application/json"},
        }
        if transport is not None:
            client_kwargs["transport"] = transport
        self._http = httpx.Client(**client_kwargs)

    def close(self) -> None:
        """Closes the underlying HTTPX connection pool."""
        self._http.close()

    def with_role(self, role: Optional[ErpRole]) -> ErpApiClient:
        """
        Returns a client view configured for the given RBAC role, sharing
        the JWT token cache and HTTP transport layer (DRY principle).
        """
        return ErpApiClient(
            settings=self.settings,
            default_role=role,
            token_cache=self._token_cache,
            transport=self._transport,
        )

    def login(self, username: str, password: str) -> httpx.Response:
        """Executes a direct POST /api/auth/login request."""
        return self._http.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )

    def get_token_for_role(self, role: ErpRole) -> str:
        """Fetches and caches a Bearer JWT access token for the specified system role."""
        if role not in self._token_cache:
            creds = ROLE_ACCOUNTS[role]
            response = self.login(creds.username, creds.password)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Authentication failed for role '{role.value}': "
                    f"HTTP {response.status_code} - {response.text}"
                )
            parsed = TokenResponseModel.model_validate(response.json())
            self._token_cache[role] = parsed.accessToken
        return self._token_cache[role]

    def _build_headers(
        self,
        role: Optional[ErpRole],
        authenticated: bool,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {}
        effective_role = role if role is not None else self.default_role
        if authenticated and effective_role is not None:
            token = self.get_token_for_role(effective_role)
            headers["Authorization"] = f"Bearer {token}"
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def get(
        self,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        role: Optional[ErpRole] = None,
        authenticated: bool = True,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Sends an HTTP GET request with automatic Bearer JWT token injection."""
        req_headers = self._build_headers(role=role, authenticated=authenticated, extra_headers=headers)
        return self._http.get(path, params=params, headers=req_headers)

    def post(
        self,
        path: str,
        *,
        json: Optional[Any] = None,
        role: Optional[ErpRole] = None,
        authenticated: bool = True,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        """Sends an HTTP POST request with a JSON payload and automatic Bearer JWT token."""
        req_headers = self._build_headers(role=role, authenticated=authenticated, extra_headers=headers)
        return self._http.post(path, json=json, headers=req_headers)
