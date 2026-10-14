#!/usr/bin/env python3
"""Single-process Mini-SIEM web application.

Run:
    python server.py
Then open http://127.0.0.1:8000
"""
from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from siem.engine import analyze
from siem.report import to_json, to_text

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
LOG_DIR = ROOT / "sample_logs"
REPORT_FILE = ROOT / "report.json"
DEFAULT_WORKERS = max(1, min(4, os.cpu_count() or 1))


def run_analysis():
    logs = sorted(str(p) for p in LOG_DIR.glob("*.log"))
    if not logs:
        raise RuntimeError(f"No .log files found in {LOG_DIR}")
    workers = DEFAULT_WORKERS
    result = analyze(logs, workers=workers)
    REPORT_FILE.write_text(to_json(result), encoding="utf-8")
    return result


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def _send_json(self, payload, status=200):
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/report":
            try:
                if REPORT_FILE.exists():
                    payload = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
                else:
                    payload = json.loads(to_json(run_analysis()))
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
            return
        if path == "/api/health":
            self._send_json({"ok": True, "project": "Mini-SIEM"})
            return
        if path == "/api/logs":
            self._send_json({"logs": [p.name for p in sorted(LOG_DIR.glob("*.log"))]})
            return
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/analyze":
            try:
                result = run_analysis()
                self._send_json(json.loads(to_json(result)))
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
            return
        self.send_error(404, "Not Found")

    def log_message(self, fmt, *args):
        print(f"[web] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    os.chdir(ROOT)
    # Analyze once before the browser opens, so report.json is real and current.
    try:
        result = run_analysis()
        print(f"Analyzed {result.events:,} events -> {len(result.alerts)} alerts -> {len(result.incidents)} incidents")
    except Exception as exc:
        print(f"Startup analysis failed: {exc}", file=sys.stderr)
        raise

    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("\nMini-SIEM dashboard is running")
    print("Open: http://127.0.0.1:8000")
    print("Refresh/Analyze button calls the real Mini-SIEM engine.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mini-SIEM...")
    finally:
        server.server_close()
