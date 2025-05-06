# create http api with 1 endpoint without using flask

import http.server
import socketserver
import json

# Define the port
PORT = 8000

# Create a custom request handler
class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/hello':
            # Set response headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Create response data
            response_data = {
                'message': 'Hello, World!',
                'status': 'success'
            }

            # Send the response
            self.wfile.write(json.dumps(response_data).encode())
        else:
            # Handle 404 for other paths
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

# Create and start the server
with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print(f"API endpoint: http://localhost:{PORT}/api/hello")
    httpd.serve_forever()
