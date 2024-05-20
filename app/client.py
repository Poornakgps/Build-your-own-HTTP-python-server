import socket

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 4221))
        s.sendall(b'Hello, server')
        data = s.recv(1024)
        print('Received', repr(data))

if __name__ == "__main__":
    main()
