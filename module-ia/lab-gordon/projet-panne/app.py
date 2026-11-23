"""Mini serveur HTTP pour le lab A1 (Gordon)."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Gestionnaire(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bonjour depuis le lab A1".encode("utf-8"))


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Gestionnaire).serve_forever()
