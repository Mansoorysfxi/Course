"""A zero-dependency toy "backend" for Exercise 05 -- built on Python's
standard-library http.server so this exercise needs no pip install and
no FastAPI at all. The point of this exercise is Nginx's reverse-proxy
configuration, not the backend itself -- keeping the backend trivial
means any bug you hit is genuinely about Nginx, not accidentally about
the app behind it.

Run with: python3 toy_backend.py
Listens on 127.0.0.1:5000 only (deliberately, per
lessons/04-networking-ports-and-ips.md -- only Nginx, on the same
machine, should ever talk to this directly).

Every request gets back a small JSON body reporting exactly which path
this backend itself received -- which is the entire diagnostic tool this
exercise needs to catch the proxy_pass trailing-slash mistake
lessons/06-nginx-and-reverse-proxies.md described: if Nginx strips or
rewrites the path before forwarding, this response will show it plainly.
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {
                "message": "toy_backend received this exact path:",
                "path_received": self.path,
            }
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Quieter default logging -- still prints one line per request,
        # just without http.server's default extra verbosity.
        print(f"toy_backend: {self.address_string()} - {format % args}")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5000), Handler)
    print("toy_backend listening on http://127.0.0.1:5000 (Ctrl+C to stop)")
    server.serve_forever()
