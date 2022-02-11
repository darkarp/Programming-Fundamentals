import socket
from com import Server

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, port = ("127.0.0.1", 8080)
    s.bind((host, port))
    s.listen()
    print("[+] Listening...")
    conn, addr = s.accept()
    server = Server(conn)
    print(f"[i] Got connection from: {addr[0]}")
    while server.process(input("cmd: ").strip()):
        pass