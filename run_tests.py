#!/usr/bin/env python3
"""
CLI Test Runner & Orchestrator for the Manufacturing ERP REST API test suite.

Allows running individual team member test suites (aleksander / lukasz) or the
complete combined suite, automatically generating a self-contained HTML report.

Usage examples:
    python run_tests.py                      # Runs Aleksander's 8 API tests by default
    python run_tests.py --suite aleksander   # Runs Aleksander Kazmierczak's test suite
    python run_tests.py --suite lukasz       # Runs Lukasz Murza's test suite
    python run_tests.py --suite all          # Runs all team API test suites
    python run_tests.py --base-url http://localhost:8081
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
from typing import Sequence

import pytest

SUITE_FILES: dict[str, list[str]] = {
    "aleksander": ["tests/test_api_aleksander.py"],
    "lukasz": ["tests/test_api_lukasz.py"],
    "all": ["tests/test_api_aleksander.py", "tests/test_api_lukasz.py"],
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="REST API Test Orchestrator for Manufacturing ERP."
    )
    parser.add_argument(
        "--suite",
        choices=["aleksander", "lukasz", "all"],
        default="aleksander",
        help="Select which test suite to execute (default: aleksander).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Target ERP server base URL (e.g. http://localhost:8081). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--html-report",
        default="reports/api_test_report.html",
        help="Output path for the generated HTML test report.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    if args.base_url:
        os.environ["ERP_BASE_URL"] = args.base_url

    report_path = pathlib.Path(args.html_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    target_files = SUITE_FILES[args.suite]
    pytest_args = [
        *target_files,
        "-v",
        f"--html={report_path}",
        "--self-contained-html",
    ]

    print("=" * 78)
    print(f" Manufacturing ERP REST API Test Orchestrator (Suite: {args.suite.upper()})")
    print("=" * 78)
    exit_code = pytest.main(pytest_args)
    print("-" * 78)
    print(f" HTML report saved to: {report_path.resolve()}")
    print("=" * 78)
    return int(exit_code)


if __name__ == "__main__":
    sys.exit(main())
