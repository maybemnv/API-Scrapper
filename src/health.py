import http.server
import json
import threading


class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "api-sniffer"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        pass  # suppress log output


def start_health_server(port: int = 8080) -> http.server.HTTPServer:
    server = http.server.HTTPServer(("127.0.0.1", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


if __name__ == "__main__":
    start_health_server()
    print("Health server running on port 8080")
    threading.Event().wait()
