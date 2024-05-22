import http.server
import socketserver
import gzip
import os
import shutil
from io import BytesIO

DIRECTORY = "/tmp/data/codecrafters.io/http-server-ttester/"  # Specify the directory for file operations

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/echo/"):
            self.handle_echo()
        elif self.path.startswith("/files/"):
            self.handle_get_file()
        elif self.path == "/user-agent":
            self.handle_user_agent()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith("/files/"):
            self.handle_post_file()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_echo(self):
        message = self.path[len("/echo/"):]
        accept_encoding = self.headers.get('Accept-Encoding', '')
        if 'gzip' in accept_encoding:
            self.send_response(200)
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Type', 'text/plain')
            gzipped_message = gzip.compress(message.encode('utf-8'))
            self.send_header('Content-Length', str(len(gzipped_message)))
            self.end_headers()
            self.wfile.write(gzipped_message)
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(message)))
            self.end_headers()
            self.wfile.write(message.encode('utf-8'))

    def handle_post_file(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        file_path = self.path[len("/files/"):]
        full_path = os.path.join(DIRECTORY, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as f:
            f.write(post_data)
        
        self.send_response(201)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def handle_get_file(self):
        file_path = self.path[len("/files/"):]
        full_path = os.path.join(DIRECTORY, file_path)
        
        if os.path.exists(full_path):
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(os.path.getsize(full_path)))
            self.end_headers()
            with open(full_path, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
        else:
            self.send_response(404)
            self.send_header('Content-Length', '0')
            self.end_headers()

    def handle_user_agent(self):
        user_agent = self.headers.get('User-Agent', '')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(user_agent)))
        self.end_headers()
        self.wfile.write(user_agent.encode('utf-8'))

    def log_message(self, format, *args):
        return  # Disable logging for cleaner test output


if __name__ == "__main__":
    PORT = 4221
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()
