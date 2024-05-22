# Uncomment this to pass the first stage
import socket
import re
class Request(object):
    def __init__(self, data) -> None:
        data_str = data.decode()
        lines = data_str.split("\r\n")
        method, path, version = lines[0].split()
        self.method = method
        self.path = path
        self.version = version
        self.user_agent = re_extract(lines[2], r"User-Agent: (.*)")
class Response(object):
    def __init__(self, status_code, data) -> None:
        self.status_code = status_code
        self.data = data
        self.status_dict = {200: "OK", 404: "Not Found"}
    def encode(self) -> bytes:
        resp_str = "HTTP/1.1 {status_code} {status}\r\nContent-Type: text/plain\r\nContent-Length: {len}\r\n\r\n{body}".format(
            status_code=self.status_code,
            status=self.status_dict[self.status_code],
            len=len(self.data),
            body=self.data,
        )
        return resp_str.encode()
def re_extract(s, pattern):
    search = re.search(pattern, s)
    if search:
        return search.group(1)
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        try:
            conn, addr = server_socket.accept()  # wait for client
            with conn:
                print("Connected by", addr)
                data = conn.recv(1024)
                print("data: %s" % data)
                req = Request(data)
                try:
                    if req.path == "/":
                        resp = "HTTP/1.1 200 OK\r\n\r\n"
                    elif "echo" in req.path:
                        arg = re_extract(req.path, r"/echo/(.*)")
                        # print("arg=%s" % arg)
                        resp = Response(200, arg)
                    elif req.path == "/user-agent":
                        resp = Response(200, req.user_agent)
                    else:
                        raise Exception("not found")
                except Exception:
                    resp = "HTTP/1.1 404 Not Found\r\n\r\n"
                conn.send(resp.encode())
        except Exception as e:
            print("[error] <{}>{}".format(e.__class__.__name__, e))
if __name__ == "__main__":
    main()