"""
Lightweight Reverse-Proxy + SPA Static Server for Frontend E2E Testing (SRP).

Serves the compiled React 19 + Mantine v9 Single-Page Application from
`ERPSystem/frontend/dist` with HTML5 History API fallback (`index.html`), while
reverse-proxying all `/api/*`, `/v3/api-docs*`, and `/actuator/*` calls directly
to the active ERP backend (either the live Spring Boot + PostgreSQL 16 server on
`:8080` or the local reference server).
"""

from __future__ import annotations

import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

import httpx

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "ERPSystem" / "frontend" / "dist"

MIME_OVERRIDES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-encoding",
    "content-length",
}


class _SpaReverseProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler serving SPA static files and reverse-proxying /api/* requests."""

    backend_base_url: str = "http://localhost:8080"
    backend_transport: Optional[httpx.BaseTransport] = None
    dist_dir: Path = FRONTEND_DIST_DIR

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        # Suppress noisy access logs during automated Playwright test execution
        pass

    def _is_api_request(self) -> bool:
        path = urlsplit(self.path).path
        return path.startswith(("/api/", "/api", "/v3/api-docs", "/actuator/"))

    def _proxy_to_backend(self, method: str) -> None:
        target_url = f"{self.backend_base_url.rstrip('/')}{self.path}"
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length > 0 else None

        forward_headers: dict[str, str] = {}
        for key, val in self.headers.items():
            if key.lower() not in HOP_BY_HOP_HEADERS and key.lower() != "host":
                forward_headers[key] = val

        try:
            with httpx.Client(transport=self.backend_transport, timeout=15.0) as client:
                resp = client.request(
                    method=method,
                    url=target_url,
                    headers=forward_headers,
                    content=body,
                )
        except httpx.HTTPError as exc:
            error_bytes = f'{{"title":"Bad Gateway","status":502,"detail":"{exc}"}}'.encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/problem+json")
            self.send_header("Content-Length", str(len(error_bytes)))
            self.end_headers()
            self.wfile.write(error_bytes)
            return

        payload = resp.content
        self.send_response(resp.status_code)
        for key, val in resp.headers.multi_items():
            if key.lower() not in HOP_BY_HOP_HEADERS:
                self.send_header(key, val)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload and method != "HEAD":
            self.wfile.write(payload)

    def _serve_static_or_spa_index(self) -> None:
        parsed_path = urlsplit(self.path).path.lstrip("/")
        candidate = (self.dist_dir / parsed_path).resolve()

        # Prevent path traversal and fallback to index.html for client-side React Router paths
        if not str(candidate).startswith(str(self.dist_dir.resolve())) or not candidate.is_file():
            candidate = self.dist_dir / "index.html"

        if not candidate.is_file():
            msg = b"Frontend build not found in ERPSystem/frontend/dist. Run 'npm run build'."
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return

        data = candidate.read_bytes()
        ext = candidate.suffix.lower()
        content_type = MIME_OVERRIDES.get(ext) or mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy_to_backend("GET")
        else:
            self._serve_static_or_spa_index()

    def do_POST(self) -> None:  # noqa: N802
        self._proxy_to_backend("POST")

    def do_PUT(self) -> None:  # noqa: N802
        self._proxy_to_backend("PUT")

    def do_DELETE(self) -> None:  # noqa: N802
        self._proxy_to_backend("DELETE")


class ErpFrontendSpaServer:
    """Lifecycle manager for the local SPA + Reverse-Proxy server used by Playwright tests."""

    def __init__(
        self,
        backend_base_url: str,
        host: str = "127.0.0.1",
        port: int = 0,
        dist_dir: Path = FRONTEND_DIST_DIR,
        backend_transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.backend_base_url = backend_base_url
        self.host = host
        self.port = port
        self.dist_dir = dist_dir
        self.backend_transport = backend_transport
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def base_url(self) -> str:
        if self._httpd is None:
            raise RuntimeError("ErpFrontendSpaServer has not been started yet")
        actual_port = self._httpd.server_address[1]
        return f"http://{self.host}:{actual_port}"

    def start(self) -> str:
        """Starts the SPA + Reverse-Proxy server in a daemon thread and returns its base URL."""

        class BoundHandler(_SpaReverseProxyHandler):
            pass

        BoundHandler.backend_base_url = self.backend_base_url
        BoundHandler.backend_transport = self.backend_transport
        BoundHandler.dist_dir = self.dist_dir

        self._httpd = ThreadingHTTPServer((self.host, self.port), BoundHandler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="ErpFrontendSpaServer",
            daemon=True,
        )
        self._thread.start()
        return self.base_url

    def stop(self) -> None:
        """Cleanly shuts down the SPA HTTP server."""
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
