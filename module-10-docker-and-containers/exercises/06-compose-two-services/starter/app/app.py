import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import redis

# REDIS_HOST is read from an environment variable -- your docker-compose.yml
# (see INSTRUCTIONS.md) is responsible for setting it to the correct
# service name so this resolves at all. See lessons/04-docker-networking.md.
redis_host = os.environ.get("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/check":
            query = parse_qs(parsed.query)
            quest = query.get("quest", ["unknown-quest"])[0]
            count = r.incr(f"quest-checks:{quest}")
            body = f"'{quest}' has been checked {count} time(s).\n"
        else:
            body = "Usage: GET /check?quest=<quest-name>\n"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())


HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
