"""
Central test environment configuration for the REST API test suite (SRP / DRY).

Provides System Under Test (SUT) connection settings and predefined RBAC role
accounts matching UserSeeder.java.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class ErpRole(str, Enum):
    """User roles defined in the IAM module of the Manufacturing ERP system."""

    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    WAREHOUSE = "warehouse"
    SALES = "sales"
    HR = "hr"
    GUEST = "guest"


@dataclass(frozen=True)
class RoleCredentials:
    """Authentication credentials for a seeded test account (password == username)."""

    username: str
    password: str
    expected_roles: tuple[str, ...]


ROLE_ACCOUNTS: dict[ErpRole, RoleCredentials] = {
    ErpRole.ADMIN: RoleCredentials(
        username="admin",
        password="admin",
        expected_roles=("ACCOUNTANT", "ADMIN", "HR", "SALES", "WAREHOUSE"),
    ),
    ErpRole.ACCOUNTANT: RoleCredentials(
        username="accountant",
        password="accountant",
        expected_roles=("ACCOUNTANT",),
    ),
    ErpRole.WAREHOUSE: RoleCredentials(
        username="warehouse",
        password="warehouse",
        expected_roles=("WAREHOUSE",),
    ),
    ErpRole.SALES: RoleCredentials(
        username="sales",
        password="sales",
        expected_roles=("SALES",),
    ),
    ErpRole.HR: RoleCredentials(
        username="hr",
        password="hr",
        expected_roles=("HR",),
    ),
    ErpRole.GUEST: RoleCredentials(
        username="guest",
        password="guest",
        expected_roles=(),
    ),
}


@dataclass(frozen=True)
class ApiSettings:
    """HTTP client configuration parameters for API tests."""

    base_url: str
    timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls) -> ApiSettings:
        """Loads configuration from environment variables with sensible defaults."""
        base_url = os.getenv("ERP_BASE_URL", "http://localhost:8081").rstrip("/")
        timeout = float(os.getenv("ERP_HTTP_TIMEOUT", "10.0"))
        return cls(base_url=base_url, timeout_seconds=timeout)
