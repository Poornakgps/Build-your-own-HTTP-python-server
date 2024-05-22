# Uncomment this to pass the first stage
import socket
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    
    conn, addr = server_socket.accept()  # wait for client
    
    data = conn.recv(1024).decode("utf-8")
    
    path = data.split(" ")


    # if path[1] == "/":
        
    #     resp = "HTTP/1.1 200 OK\r\n\r\n"
    #     conn.send(resp.encode())
    #     # conn.sendall(b"Hello, World!")
        
    # elif path[1].startswith("/echo"):
    #     random_path = path[1][6:]
    #     response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(random_path)}\r\n\r\n{random_path}\r\n"
    #     conn.send(response.encode())
    #     print(random_path)
    # else:
    #     conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        # conn.sendall(b"404 Not Found")
    # print(data)
    print(path)
    user_agent = path[5]
    length = 0
    user_agent = user_agent.split("\r\n")
    length = len(user_agent[0])

    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{user_agent[0]}\r\n"
    conn.send(response.encode())
    # print("Connection from", addr) # Connection from ('127.0.0.1', 34826)
    
    # print(conn) # <socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 4221), raddr=('127.0.0.1', 34834)>
    
    #  print("Received", conn.recv(1024)) # Received b'GET / HTTP/1.1\r\nHost: localhost:4221\r\nUser-Agent: curl/7.81.0\r\nAccept: */*\r\n\r\n'
    
    #2 server_socket.accept()[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")  # wait for client
    
if __name__ == "__main__":
    main()