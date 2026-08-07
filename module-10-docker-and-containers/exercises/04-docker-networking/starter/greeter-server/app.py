from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Greetings, traveler! The greeter-server received your request.\n")


HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
