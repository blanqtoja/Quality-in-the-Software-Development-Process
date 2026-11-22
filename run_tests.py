#!/usr/bin/env python3
"""
CLI Test Runner & Orchestrator for the Manufacturing ERP REST API & Frontend E2E test suites.

Allows running individual team member test suites (`aleksander` / `lukasz` / `all`)
and selecting the test layer (`api` / `frontend` / `all`), automatically generating
a self-contained HTML report.

Usage examples:
    python run_tests.py                                   # Runs Aleksander's API (8) + Frontend (4) tests
    python run_tests.py --layer frontend                  # Runs Aleksander's 4 Frontend E2E tests
    python run_tests.py --layer api                       # Runs Aleksander's 8 REST API tests
    python run_tests.py --suite lukasz --layer frontend   # Runs Lukasz Murza's Frontend E2E suite
    python run_tests.py --suite all --layer all           # Runs all team API & Frontend suites
    python run_tests.py --base-url http://localhost:8080  # Points against live Java server
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
from typing import Sequence

ROOT = pathlib.Path(__file__).resolve().parent

SUITE_MATRIX: dict[str, dict[str, list[str]]] = {
    "aleksander": {
        "api": ["tests/test_api_aleksander.py"],
        "frontend": ["tests/test_frontend_aleksander.py"],
        "all": ["tests/test_api_aleksander.py", "tests/test_frontend_aleksander.py"],
    },
    "lukasz": {
        "api": ["tests/test_api_lukasz.py"],
        "frontend": ["tests/test_frontend_lukasz.py"],
        "all": ["tests/test_api_lukasz.py", "tests/test_frontend_lukasz.py"],
    },
    "all": {
        "api": ["tests/test_api_aleksander.py", "tests/test_api_lukasz.py"],
        "frontend": ["tests/test_frontend_aleksander.py", "tests/test_frontend_lukasz.py"],
        "all": [
            "tests/test_api_aleksander.py",
            "tests/test_frontend_aleksander.py",
            "tests/test_api_lukasz.py",
            "tests/test_frontend_lukasz.py",
        ],
    },
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="REST API & Frontend E2E Test Orchestrator for Manufacturing ERP."
    )
    parser.add_argument(
        "--suite",
        choices=["aleksander", "lukasz", "all"],
        default="aleksander",
        help="Select which team member's test suite to execute (default: aleksander).",
    )
    parser.add_argument(
        "--layer",
        choices=["api", "frontend", "ui", "all"],
        default="all",
        help="Select which test layer to execute: api, frontend, or all (default: all).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Target ERP backend base URL (e.g. http://localhost:8080). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--frontend-url", "--ui-base-url",
        default=None,
        help="Target ERP frontend SPA URL. Auto-starts embedded SPA server if omitted.",
    )
    parser.add_argument(
        "--backend-mode", choices=["auto", "live", "reference"], default=None,
        help="live requires ERP; reference is an explicit test double; auto preserves legacy detection.",
    )
    parser.add_argument("--collect-only", action="store_true", help="Collect tests without execution or overwriting the HTML report.")
    parser.add_argument("--ui-channel", choices=["chrome", "msedge", "chromium"], help="Select the UI browser explicitly.")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run Playwright browser in headed (visible window) mode.",
    )
    parser.add_argument(
        "--html-report",
        default="reports/api_test_report.html",
        help="Output path for the generated HTML test report.",
    )
    args = parser.parse_args(argv)
    if args.layer == "ui":
        args.layer = "frontend"
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        import pytest
    except ModuleNotFoundError as error:
        print(f"Missing dependency: {error.name}. Install requirements-test.txt.", file=sys.stderr)
        return 4

    if args.base_url:
        os.environ["ERP_BASE_URL"] = args.base_url
    if args.frontend_url:
        os.environ["ERP_FRONTEND_URL"] = args.frontend_url
    if args.headed:
        os.environ["ERP_HEADED"] = "1"
    if args.backend_mode:
        os.environ["ERP_BACKEND_MODE"] = args.backend_mode
    if args.ui_channel:
        os.environ["ERP_BROWSER_CHANNEL"] = args.ui_channel

    report_path = pathlib.Path(args.html_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    target_files = [str(ROOT / path) for path in SUITE_MATRIX[args.suite][args.layer]]
    pytest_args = [
        *target_files,
        "-v",
    ]
    if args.collect_only:
        pytest_args.append("--collect-only")
    else:
        pytest_args.extend([f"--html={report_path}", "--self-contained-html"])

    print("=" * 78)
    print(
        f" Manufacturing ERP Test Orchestrator "
        f"(Suite: {args.suite.upper()} | Layer: {args.layer.upper()})"
    )
    print("=" * 78)
    exit_code = pytest.main(pytest_args)
    print("-" * 78)
    if not args.collect_only and report_path.exists():
        print(f" HTML report path: {report_path.resolve()}")
    print("=" * 78)
    return int(exit_code)


if __name__ == "__main__":
    sys.exit(main())
