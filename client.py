import time
import socket
from com import Client


if __name__ == "__main__":
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, port = "127.0.0.1", 8080
    while(True):
        try:
            conn.connect((host, port))
            break
        except ConnectionRefusedError:
            time.sleep(10)
    client = Client(conn)
    while client.process((buf := client.receive(decode=False))):
        pass