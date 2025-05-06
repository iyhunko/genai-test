# create http api with 1 endpoint without using flask

import http.server
import socketserver
import json
import os

# Define constants
HTTP_OK = 200
HTTP_NOT_FOUND = 404
CONTENT_TYPE_JSON = 'application/json'

# Get port from environment variable or use default
PORT = int(os.environ.get('API_PORT', 8000))

# Create a custom request handler
class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        content_type = CONTENT_TYPE_JSON
        path = self.path

        # Route request to appropriate handler
        if path == '/api/hello':
            status_code, response_data = self._handle_hello_endpoint()
        else:
            status_code, response_data = self._handle_not_found()

        # Send the response
        self._send_json_response(status_code, response_data, content_type)

    def _handle_hello_endpoint(self):
        """Handle the /api/hello endpoint."""
        return HTTP_OK, {
            'message': 'Hello, World!',
            'status': 'success'
        }

    def _handle_not_found(self):
        """Handle requests to non-existent endpoints."""
        return HTTP_NOT_FOUND, {'error': 'Not found'}

    def _send_json_response(self, status_code, response_data, content_type):
        """Send a JSON response with the given status code and data."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())


# Create and start the server
with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print(f"API endpoint: http://localhost:{PORT}/api/hello")
    httpd.serve_forever()
