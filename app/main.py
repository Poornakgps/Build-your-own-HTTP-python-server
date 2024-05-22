import socket
import threading
import argparse
import os
import gzip

# Argument parser setup
parser = argparse.ArgumentParser(description="HTTP Server")
parser.add_argument("--directory", dest="directory", required=True, help="Directory to serve files from")
args = parser.parse_args()
directory = args.directory

# Request class to parse incoming HTTP requests
class Request:
    def __init__(self, request: bytes):
        request_string = request.decode()
        body_split = request_string.split("\r\n\r\n", 1)
        lines = body_split[0].split("\r\n")
        
        # Parse request line
        status = lines[0].split()
        self.method = status[0]
        self.path = status[1]
        self.version = status[2]
        
        # Parse headers
        self.headers = {}
        for x in range(1, len(lines)):
            if ": " in lines[x]:
                key, value = lines[x].split(": ", 1)
                self.headers[key.lower()] = value
        
        # Parse body
        self.body = body_split[1] if len(body_split) > 1 else ""

# Main function to start the server
def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print(f"Server started at localhost:4221 serving directory {directory}")

    while True:
        client_socket, client_address = server_socket.accept()  # Wait for client
        print(f"Connection from {client_address}")
        threading.Thread(target=request_handler, args=(client_socket,), daemon=True).start()

# Function to handle client requests
def request_handler(client_socket):
    try:
        data = client_socket.recv(1024)
        if not data:
            client_socket.close()
            return
        
        request = Request(data)
        print(f"Received request: {request.method} {request.path}")
        
        path_resources = request.path.split("/")
        
        if len(path_resources) > 1 and path_resources[1] == "echo" and len(path_resources) == 3 and request.method == "GET":
            handle_echo_request(client_socket, request, path_resources[2])
        elif len(path_resources) > 1 and path_resources[1] == "user-agent" and request.method == "GET":
            handle_user_agent_request(client_socket, request)
        elif len(path_resources) > 1 and path_resources[1] == "files":
            handle_files_request(client_socket, request, path_resources[2])
        else:
            client_socket.sendall(build_response("404 Not Found", "Content-Length: 0"))
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

# Function to handle /echo requests
def handle_echo_request(client_socket, request, message):
    if "accept-encoding" not in request.headers or "gzip" not in request.headers["accept-encoding"]:
        client_socket.sendall(build_response("200 OK", f"Content-Type: text/plain\r\nContent-Length: {len(message)}", message.encode()))
    else:
        response_body = gzip.compress(message.encode())
        headers = f"Content-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}"
        client_socket.sendall(build_response("200 OK", headers, response_body))

# Function to handle /user-agent requests
def handle_user_agent_request(client_socket, request):
    user_agent = request.headers.get("user-agent", "")
    client_socket.sendall(build_response("200 OK", f"Content-Type: text/plain\r\nContent-Length: {len(user_agent)}", user_agent.encode()))

# Function to handle /files requests
def handle_files_request(client_socket, request, filename):
    if request.method == "GET":
        try:
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as f:
                file_content = f.read()
                client_socket.sendall(build_response("200 OK", f"Content-Type: application/octet-stream\r\nContent-Length: {len(file_content)}", file_content))
        except FileNotFoundError:
            client_socket.sendall(build_response("404 Not Found", "Content-Length: 0"))
        except Exception as e:
            print(f"Error reading file: {e}")
            client_socket.sendall(build_response("500 Internal Server Error", "Content-Length: 0"))
    elif request.method == "POST":
        try:
            file_path = os.path.join(directory, filename)
            with open(file_path, "wb") as f:
                f.write(request.body.encode())
                client_socket.sendall(build_response("201 Created", "Content-Length: 0"))
        except Exception as e:
            print(f"Error writing file: {e}")
            client_socket.sendall(build_response("500 Internal Server Error", "Content-Length: 0"))

# Function to build HTTP responses
def build_response(status: str, headers: str, body: bytes = b"") -> bytes:
    return f"HTTP/1.1 {status}\r\n{headers}\r\n\r\n".encode() + body

# Entry point of the script
if __name__ == "__main__":
    main()
