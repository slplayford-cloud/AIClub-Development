"""A tiny one-shot localhost web server that catches the OAuth redirect.

The Google sign-in flow ends with the browser being redirected to
``http://localhost:<port>/?code=...``. A CLI can't receive a browser redirect
directly, so we briefly run a local HTTP server, let the browser hit it, pull the
``code`` (or ``error``) out of the query string, and shut down.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from typing import Callable, cast

_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>AI Club sign-in</title></head>
<body style="font-family:system-ui,sans-serif;text-align:center;padding-top:4rem">
<h2>{heading}</h2><p>{message}</p></body></html>"""


class _CallbackServer(HTTPServer):
    """HTTPServer that records the captured code/error and signals when done."""

    auth_code: str | None = None
    auth_error: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.done = threading.Event()


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        server = cast(_CallbackServer, self.server)
        params = parse_qs(urlparse(self.path).query)
        if "code" in params:
            server.auth_code = params["code"][0]
            self._respond(200, "✅ Signed in", "You can close this tab and return to the terminal.")
            server.done.set()
        elif "error" in params:
            server.auth_error = (
                params.get("error_description") or params.get("error") or ["unknown error"]
            )[0]
            self._respond(400, "❌ Sign-in failed", server.auth_error)
            server.done.set()
        else:
            # Stray request (e.g. /favicon.ico) — ignore, keep waiting.
            self._respond(204, "", "")

    def _respond(self, status: int, heading: str, message: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if heading:
            self.wfile.write(_PAGE.format(heading=heading, message=message).encode())

    def log_message(self, format: str, *args) -> None:  # silence default logging
        pass


def wait_for_callback(
    host: str,
    port: int,
    on_ready: Callable[[], None],
    timeout: float = 300.0,
) -> tuple[str | None, str | None]:
    """Run the callback server and block until the redirect arrives.

    ``on_ready`` is called once the server is listening (that's when we open the
    browser, so we never miss a fast redirect). Returns ``(code, error)`` — one
    of them is set, or ``(None, <reason>)`` on timeout.
    """
    server = _CallbackServer((host, port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        on_ready()
        completed = server.done.wait(timeout)
    finally:
        server.shutdown()
        server.server_close()

    if not completed:
        return None, "timed out waiting for the browser redirect"
    return server.auth_code, server.auth_error
