"""
Shared assertion helpers for the REST API test suite (DRY and SRP).

Provides consistent verification of HTTP status codes, Content-Type headers,
RFC 9457 Problem Details error contracts (application/problem+json), Pydantic
schema validation, and exact financial precision using decimal.Decimal.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Type, TypeVar

import httpx
from pydantic import BaseModel

from tests.models import ProblemDetailModel

TModel = TypeVar("TModel", bound=BaseModel)


def assert_status_code(response: httpx.Response, expected_status: int) -> None:
    """Asserts the HTTP response status code with a detailed diagnostic failure message."""
    assert response.status_code == expected_status, (
        f"Unexpected HTTP status code for {response.request.method} {response.request.url}: "
        f"expected {expected_status}, got {response.status_code}. "
        f"Response body: {response.text}"
    )


def assert_valid_model(
    response: httpx.Response,
    model_cls: Type[TModel],
    *,
    expected_status: int = 200,
) -> TModel:
    """
    Verifies the HTTP status code, checks for a JSON Content-Type header,
    and validates the response payload against the given Pydantic model class.
    """
    assert_status_code(response, expected_status)
    content_type = response.headers.get("content-type", "")
    assert "json" in content_type.lower(), (
        f"Expected Content-Type header containing 'json', got: '{content_type}'"
    )
    return model_cls.model_validate(response.json())


def assert_problem_detail(
    response: httpx.Response,
    *,
    expected_status: int,
    expected_title: Optional[str] = None,
    detail_contains: Optional[str] = None,
) -> ProblemDetailModel:
    """
    Verifies an RFC 9457 Problem Details error response (application/problem+json)
    and returns the validated ProblemDetailModel instance.
    """
    assert_status_code(response, expected_status)
    content_type = response.headers.get("content-type", "").lower()
    assert "application/problem+json" in content_type or "application/json" in content_type, (
        f"Expected RFC 9457 error format (application/problem+json), got: '{content_type}'"
    )
    problem = ProblemDetailModel.model_validate(response.json())
    assert problem.status == expected_status, (
        f"ProblemDetail 'status' field ({problem.status}) does not match HTTP status ({expected_status})"
    )
    if expected_title is not None:
        assert problem.title.lower() == expected_title.lower(), (
            f"Expected ProblemDetail title='{expected_title}', got '{problem.title}'"
        )
    if detail_contains is not None:
        assert problem.detail is not None and detail_contains.lower() in problem.detail.lower(), (
            f"Expected ProblemDetail 'detail' to contain '{detail_contains}', got: '{problem.detail}'"
        )
    return problem


def assert_decimal_equal(actual: str | Decimal, expected: str | Decimal, label: str = "amount") -> None:
    """Compares monetary or quantity values using decimal.Decimal without floating-point drift."""
    actual_dec = Decimal(str(actual))
    expected_dec = Decimal(str(expected))
    assert actual_dec == expected_dec, (
        f"Decimal mismatch ({label}): expected {expected_dec}, got {actual_dec}"
    )
