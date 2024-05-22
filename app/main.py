import socket
import threading
import os
import sys
STATUS_200 = "HTTP/1.1 200 OK\r\n"
STATUS_201 = "HTTP/1.1 201 Created\r\n\r\n"
STATUS_404 = "HTTP/1.1 404 Not Found\r\n\r\n"
# Function that defines the behaviour for handling a single client connection
def handle_connection(connection_socket, address):
    # Extract URL path - request target
    request_data = connection_socket.recv(4096).decode()
    print(f"Received chunk:\n{request_data}")
    # Parse the HTTP request
    lines = request_data.split("\r\n")
    print(lines)
    headers = {}
    for header in lines[1:]:
        if header == "":
            break
        key, value = header.split(": ")
        print(key, value)
        headers[key] = value
    start_line = lines[0]
    method, request_target, http_version = start_line.split(" ")
    print(request_data)
    request_body = lines[-1]
    if request_target == "/":
        connection_socket.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif request_target.startswith("/user-agent"):
        response = (
            f"{STATUS_200}"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(headers.get('User-Agent'))}\r\n"
            "\r\n"
            f"{headers.get('User-Agent')}"
        )
        # HTTP response
        connection_socket.sendall(response.encode())
    elif request_target.startswith("/echo"):
        endpoint = (request_target.split("/"))[-1]
        response = (
            f"{STATUS_200}"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(endpoint)}\r\n"
            "\r\n"
            f"{endpoint}"
        )
        # HTTP response
        connection_socket.sendall(response.encode())
    elif request_target.startswith("/files") and method == "GET":
        filename = (request_target.split("/"))[2]
        print(filename)
        directory = sys.argv[2]
        path = "".join([directory, filename])
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
                response = (
                    f"{STATUS_200}"
                    "Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    "\r\n"
                    f"{content}"
                )
                # HTTP response
                connection_socket.sendall(response.encode())
        else:
            connection_socket.sendall(STATUS_404.encode())
    elif request_target.startswith("/files") and method == "POST":
        filename = (request_target.split("/"))[2]
        print(filename)
        directory = sys.argv[2]
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = "".join([directory, filename])
        with open(path, "w") as file:
            file.write(request_body)
        response = f"{STATUS_201}"
        # HTTP response
        connection_socket.sendall(response.encode())
    else:
        # HTTP response
        connection_socket.sendall(STATUS_404.encode())
    connection_socket.close()
# Main function that accepts incoming connections and create threadss
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    # Create TCP server socket
    server_socket = socket.create_server(("localhost", 4221))
    # Accept different TCP connections and handle them in separate threads
    while True:
        (connection_socket, address) = server_socket.accept()  # wait for client
        print(f"Received connection from {address}")
        connection_thread = threading.Thread(
            target=handle_connection, args=(connection_socket, address)
        )
        connection_thread.start()
if __name__ == "__main__":
    main()