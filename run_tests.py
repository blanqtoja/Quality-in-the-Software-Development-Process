#!/usr/bin/env python3
"""
Common test runner for Manufacturing ERP API (pytest) and UI (Playwright).

Allows running individual team member test suites (aleksander / lukasz) or the
complete combined suite, automatically generating a self-contained HTML report.

Usage examples:
    python run_tests.py                      # Runs Aleksander's 8 API tests by default
    python run_tests.py --suite aleksander   # Runs Aleksander Kazmierczak's test suite
    python run_tests.py --suite lukasz       # Runs Lukasz Murza's test suite
    python run_tests.py --suite all          # Runs all team API test suites
    python run_tests.py --base-url http://localhost:8081
    python run_tests.py --layer ui --suite all --ui-base-url http://localhost:8081
    python run_tests.py --layer ui --suite lukasz --collect-only
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Sequence

ROOT = pathlib.Path(__file__).resolve().parent
SUITE_FILES: dict[str, list[str]] = {
    "aleksander": ["tests/test_api_aleksander.py"],
    "lukasz": ["tests/test_api_lukasz.py"],
    "all": ["tests/test_api_aleksander.py", "tests/test_api_lukasz.py"],
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="API and UI Test Orchestrator for Manufacturing ERP."
    )
    parser.add_argument("--layer", choices=["api", "ui", "all"], default="api")
    parser.add_argument("--collect-only", action="store_true", help="List tests without executing them.")
    parser.add_argument("--ui-base-url", help="Real ERP frontend URL (or ERP_UI_BASE_URL).")
    parser.add_argument("--ui-channel", choices=["chrome", "msedge"], help="Use an installed browser instead of bundled Chromium.")
    parser.add_argument(
        "--suite",
        choices=["aleksander", "lukasz", "all"],
        default=None,
        help="Select suite (default: API=aleksander, UI/all=lukasz). UI covers Lukasz only.",
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
    args = parser.parse_args(argv)
    if args.suite is None:
        args.suite = "aleksander" if args.layer == "api" else "lukasz"
    if args.layer in ("ui", "all") and args.suite == "aleksander":
        parser.error("UI is implemented only for Lukasz. Use --suite lukasz or --suite all.")
    return args


def run_api(args: argparse.Namespace) -> int:
    try:
        import pytest
    except ModuleNotFoundError as error:
        print(f"Missing API dependency: {error.name}. Install requirements-test.txt.", file=sys.stderr)
        return 4

    if args.base_url:
        os.environ["ERP_BASE_URL"] = args.base_url

    report_path = pathlib.Path(args.html_report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    target_files = [str(ROOT / path) for path in SUITE_FILES[args.suite]]
    pytest_args = [
        *target_files,
        "-v",
        f"--html={report_path}",
        "--self-contained-html",
    ]
    if args.collect_only:
        pytest_args.append("--collect-only")

    print("=" * 78)
    print(f" Manufacturing ERP REST API Test Orchestrator (Suite: {args.suite.upper()})")
    print("=" * 78)
    exit_code = pytest.main(pytest_args)
    print("-" * 78)
    if report_path.exists():
        print(f" HTML report path: {report_path.resolve()}")
    print("=" * 78)
    return int(exit_code)


def run_ui(args: argparse.Namespace) -> int:
    node = shutil.which("node")
    if node is None:
        print("Node.js 20+ is required for UI tests.", file=sys.stderr)
        return 4
    environment = os.environ.copy()
    if args.ui_base_url:
        environment["ERP_UI_BASE_URL"] = args.ui_base_url
    if args.ui_channel:
        environment["ERP_UI_CHANNEL"] = args.ui_channel
    # Resolve the local installation rather than invoking npx, which can download another version.
    resolved = subprocess.run(
        [node, "-p", "require.resolve('playwright/package.json')"],
        cwd=ROOT, env=environment, capture_output=True, text=True,
    )
    if resolved.returncode:
        print("Playwright is missing. Run npm install and npx playwright install chromium.", file=sys.stderr)
        return 4
    cli = pathlib.Path(resolved.stdout.strip()).with_name("cli.js")
    command = [node, str(cli), "test", "--config", str(ROOT / "playwright.config.cjs")]
    if args.suite != "all":
        command.extend(["--grep", f"@{args.suite}"])
    if args.collect_only:
        command.append("--list")
    return subprocess.run(command, cwd=ROOT, env=environment).returncode


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    outcomes = []
    if args.layer in ("api", "all"):
        outcomes.append(run_api(args))
    if args.layer in ("ui", "all"):
        outcomes.append(run_ui(args))
    return next((code for code in outcomes if code), 0)


if __name__ == "__main__":
    sys.exit(main())
