from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
import urllib.request

HOST = os.getenv("NEXAMART_PROXY_HOST", "127.0.0.1")
PORT = int(os.getenv("NEXAMART_PROXY_PORT", "11435"))
API_TOKEN = os.getenv("NEXAMART_LLM_TOKEN", "")
OLLAMA_URL = os.getenv("NEXAMART_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")


class Proxy(BaseHTTPRequestHandler):
    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        supplied = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return bool(API_TOKEN) and hmac.compare_digest(supplied, API_TOKEN)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "online", "upstream": OLLAMA_URL, "token_configured": bool(API_TOKEN)})
        else:
            self.send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        if not self.authorized():
            self.send_json(401, {"error": "Unauthorized"})
            return
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            request = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(request, timeout=60) as response:
                self.send_json(response.status, json.loads(response.read()))
        except Exception as exc:
            self.send_json(502, {"error": "Ollama request failed", "type": type(exc).__name__})


if __name__ == "__main__":
    if not API_TOKEN:
        raise RuntimeError("NEXAMART_LLM_TOKEN must be configured before starting the proxy")
    print(f"NexaMart LLM proxy listening on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Proxy).serve_forever()
