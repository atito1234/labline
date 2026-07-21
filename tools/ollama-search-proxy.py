#!/usr/bin/env python3
"""
LabLine — tiny local CORS proxy for Ollama web search.

Browsers can't call https://ollama.com/api/web_search directly (it sends no CORS
headers), so LabLine's in-browser research fails with "Failed to fetch". This
script runs on YOUR machine, holds your Ollama API key in an environment
variable (never in the browser), forwards each search to Ollama, and returns the
result with CORS headers the browser accepts. Nothing else leaves your machine.

SETUP
  1) Get a key at https://ollama.com  ->  Settings -> Keys.
  2) Put it in an environment variable and run this file:

     Windows (PowerShell):
        $env:OLLAMA_API_KEY = "paste-your-key-here"
        python tools/ollama-search-proxy.py

     macOS / Linux:
        export OLLAMA_API_KEY="paste-your-key-here"
        python3 tools/ollama-search-proxy.py

  3) In LabLine -> AI settings:
        Enable web search:  on
        Search URL:         http://localhost:8791/search
        Search key:         leave BLANK (the proxy holds it)

Optional env vars:  PORT (default 8791), ALLOW_ORIGIN (default *).
Stdlib only — no pip installs.
"""
import os, json, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEY = os.environ.get("OLLAMA_API_KEY", "").strip()
PORT = int(os.environ.get("PORT", "8791"))
ALLOW = os.environ.get("ALLOW_ORIGIN", "*")
UPSTREAM = "https://ollama.com/api/web_search"


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOW)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def _json(self, code, payload_bytes):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if not KEY:
            self._json(500, b'{"error":"OLLAMA_API_KEY env var is not set"}')
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
        except ValueError:
            n = 0
        body = self.rfile.read(n) if n else b"{}"
        req = urllib.request.Request(
            UPSTREAM, data=body, method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + KEY},
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                self._json(200, r.read())
        except urllib.error.HTTPError as e:
            self._json(e.code, e.read())
        except Exception as e:
            self._json(502, json.dumps({"error": str(e)}).encode())

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    state = "set" if KEY else "MISSING — set OLLAMA_API_KEY"
    print(f"LabLine Ollama search proxy: http://localhost:{PORT}/search   (key: {state})")
    print("Point LabLine -> AI settings -> Search URL at the address above. Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
