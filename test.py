import unittest
import requests
import threading
import time
import os
import signal
import subprocess
import json
import socket

class APIServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the server in a separate process
        cls.server_process = subprocess.Popen(['python', 'main.py'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
        # Give the server time to start
        time.sleep(1)
        cls.base_url = "http://localhost:8000"

    @classmethod
    def tearDownClass(cls):
        # Terminate the server process
        cls.server_process.terminate()
        cls.server_process.wait()

    def test_nonexistent_endpoint(self):
        """Test that non-existent endpoints return 404."""
        response = requests.get(f"{self.base_url}/api/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data, {"error": "Not found"})

    def test_root_endpoint(self):
        """Test that the root endpoint returns 404."""
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data, {"error": "Not found"})

    def test_unsupported_method(self):
        """Test that unsupported HTTP methods are handled properly."""
        # The server only implements GET, so POST should fail
        response = requests.post(f"{self.base_url}/api/hello")
        # The default handler will return 501 Not Implemented
        self.assertEqual(response.status_code, 501)

    def test_malformed_url(self):
        """Test with malformed URL paths."""
        response = requests.get(f"{self.base_url}/api/hello/extra/segments")
        self.assertEqual(response.status_code, 404)

        response = requests.get(f"{self.base_url}/api//hello")
        self.assertEqual(response.status_code, 404)

    def test_special_characters(self):
        """Test with special characters in the URL."""
        response = requests.get(f"{self.base_url}/api/hello%20world")
        self.assertEqual(response.status_code, 404)

        response = requests.get(f"{self.base_url}/api/hello?param=value")
        self.assertEqual(response.status_code, 404)

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        def make_request():
            return requests.get(f"{self.base_url}/api/hello")

        # Create and start 10 threads to make concurrent requests
        threads = []
        results = []
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all requests were successful
        for response in results:
            self.assertEqual(response.status_code, 200)

    def test_server_port_in_use(self):
        """Test behavior when the server port is already in use."""
        # Start a socket on the same port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', 8000))
            sock.listen(1)

            # Try to start another server on the same port
            process = subprocess.Popen(['python', 'main.py'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            time.sleep(1)

            # The process should have exited with an error
            self.assertIsNotNone(process.poll())
            process.terminate()

        finally:
            sock.close()

    def test_large_request_path(self):
        """Test with an extremely long request path."""
        long_path = "/api/" + "a" * 10000
        response = requests.get(f"{self.base_url}{long_path}")
        # The server should handle this without crashing
        self.assertIn(response.status_code, [404, 414])  # 414 is URI Too Long

if __name__ == '__main__':
    unittest.main()
