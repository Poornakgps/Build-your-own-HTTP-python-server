import socket
import threading
import argparse
import os
import gzip
parser = argparse.ArgumentParser(description="takes directory")
parser.add_argument("--directory", dest="directory")
args = parser.parse_args()
directory = args.directory
class Request:
    def __init__(self, request: bytes):
        request_string = request.decode()
        body_split = request_string.split("\r\n\r\n")
        lines = body_split[0].split("\r\n")
        status = lines[0].split()
        self.method = status[0]
        self.path = status[1] 
        self.version = status[2]
        self.headers = {}
        for x in range(1, len(lines)):
            key, value = lines[x].split(": ")
            self.headers[key.lower()] = value
        self.body = body_split[1]
        
def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        client_socket, client_address = server_socket.accept() # wait for client
        threading.Thread(target=request_handler, args=(client_socket, client_address,), daemon=True).start()
def request_handler(client_socket, client_address):
    data = client_socket.recv(1024)
    request = Request(data)
    if request.path == "/":
        client_socket.sendall(build_response("200 OK", "").encode())
    path_resources = request.path.split("/")
    print(path_resources[1])
    print(len(path_resources))
    print(request.method)
    if path_resources[1] == "echo" and len(path_resources) == 3 and request.method == "GET":
        print(request.headers)
        print(request.headers.get("accept-encoding"))
        if request.headers.get("accept-encoding") is None:
            client_socket.sendall(build_response("200 OK", f"Content-Type: text/plain\r\nContent-Length: {len(path_resources[2])}", path_resources[2]).encode())
        if "gzip" in request.headers.get("accept-encoding"):
            # client_socket.sendall(build_response("200 OK", f"Content-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(path_resources[2])}", path_resources[2]).encode())
            response_body = gzip.compress(path_resources[2].encode())
            client_socket.sendall(f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n".encode() + response_body)
    if path_resources[1] == "echo" and request.method == "GET":
        client_socket.sendall(build_response("200 OK", f"Content-Type: text/plain\r\nContent-Length: {len(path_resources[2])}", path_resources[2]).encode())
    if path_resources[1] == "user-agent" and request.method == "GET":
        client_socket.sendall(build_response("200 OK", f"Content-Type: text/plain\r\nContent-Length: {len(request.headers["user-agent"])}", request.headers["user-agent"]).encode())
    if path_resources[1] == "files" and request.method == "GET":
        try:
            file_path = os.path.join(directory, path_resources[2])
            with open(file_path, "r") as f:
                file_content = f.read()
                client_socket.sendall(build_response("200 OK", f"Content-Type: application/octet-stream\r\nContent-Length: {len(file_content)}", file_content).encode())
        except Exception:
            client_socket.sendall(build_response("404 Not Found", "Content-Length: 0").encode())
    if path_resources[1] == "files" and request.method == "POST":
        try:
            file_path = os.path.join(directory, path_resources[2])
            print("File path: ", file_path)
            print("File content: ", request.body)
            with open(file_path, "w") as f:
                f.write(request.body)
                client_socket.sendall(build_response("201 Created", "Content-Length: 0").encode())
        except Exception as e:
            print("Error: ", e)
            client_socket.sendall(build_response("500 Internal Error", "Content-Length: 0").encode())
            
    else:
        client_socket.sendall(build_response("404 Not Found", "").encode())
def build_response(status: str, headers: str, body: str = "") -> str:
    return f"HTTP/1.1 {status}\r\n{headers}\r\n\r\n{body}"
if __name__ == "__main__":
    main()