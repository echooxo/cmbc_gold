import http.server
import socketserver
import urllib.request
import json
import ssl

PORT = 8080

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/price-diff':
            self.proxy_request('GET', 'https://mobile.cmbchina.com/igoldaccount/golddetail/price-diff')
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/history-price':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            self.proxy_request('POST', 'https://mobile.cmbchina.com/igoldaccount/golddetail/history-price', post_data)
        elif self.path == '/api/time-price':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            self.proxy_request('POST', 'https://mobile.cmbchina.com/igoldaccount/gold-price/time-price', post_data)
        else:
            self.send_error(404)

    def proxy_request(self, method, url, data=None):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Content-Type', 'application/json')
        # Bypass SSL verification for proxy
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                body = response.read()
                self.send_response(response.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
        except Exception as e:
            self.send_error(500, str(e))

with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
