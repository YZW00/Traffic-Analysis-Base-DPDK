import os
import json
import socket
import subprocess

class SharkdSession:
    JSONRPC_VERSION = "2.0"

    def __init__(self, addr: tuple=None, exec_name="sharkd") -> None:
        self.req_id = 1
        self.file_opened = None
        self.cached_response = {}
        if addr:
            if addr is tuple:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(addr)
        else:
            self.socket = None
            self.proc = subprocess.Popen([exec_name, "-"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=os.environ.copy())

    def load(self, filename: str) -> None:
        self.jsonrpc_request("load", {
            "file": filename
        }, no_return=True)
        self.file_opened = filename

    def close(self) -> None:
        if self.file_opened:
            self.jsonrpc_request("bye", no_return=True)
            self.file_opened = None
        if self.socket:
            self.socket.close()
        else:
            self.proc.terminate()

    def dumpconf(self) -> dict:
        return self.jsonrpc_request("dumpconf")

    def check(self) -> None:
        self.jsonrpc_request("check", no_return=True)

    def status(self) -> dict:
        return self.jsonrpc_request("status")

    def analyse(self) -> dict:
        return self.jsonrpc_request("analyse")

    def info(self) -> dict:
        return self.jsonrpc_request("info")

    def frames(self, filter="") -> dict:
        return self.jsonrpc_request("frames", {"filter": filter})

    def frame(self, frame: int, proto=True, bytes=False) -> dict:
        return self.jsonrpc_request("frame", {
            "frame": frame,
            "proto": proto,
            "bytes": bytes
        })

    def communicate(self, message: bytes) -> bytes:
        # Decode the incoming JSON message
        message_dict = json.loads(message.decode('utf-8'))
        print(f"=====Original message: {message_dict}")

        # Transform 'method' to 'req' and extract 'params' content
        transformed_message = {
            "jsonrpc": message_dict["jsonrpc"],
            "id": message_dict["id"],
            "req": message_dict["method"]
        }
        # Merge params into the root if they exist
        if "params" in message_dict:
            transformed_message.update(message_dict["params"])

        # Encode the transformed message back to bytes
        message = json.dumps(transformed_message).encode('utf-8')
        print(f"=====Transformed message: {transformed_message}")

        # Send the message and receive the response
        if self.socket:
            self.socket.send(message)
            self.socket.send(b"\n")
            response = self.socket.recv(4096)
            while not response.endswith(b"\n"):
                response += self.socket.recv(4096)
        else:
            self.proc.stdin.write(message)
            self.proc.stdin.write(b"\n")
            self.proc.stdin.flush()
            #self.proc.stdout.flush()
            #response = self.proc.stdout.readline()
            response = b""
            while True:
                line = self.proc.stdout.readline()
                response += line
                if line.strip() == b"":
                    break

        print("=====Response from process.")

        # Decode the response and handle {"err": 0} -> {"status": "OK"}
        response_dict = json.loads(response.decode('utf-8'))
        if response_dict == {"err": 0}:
            response_dict = {"status": "OK"}

        # Wrap the final response in the desired format
        final_response = {
            "jsonrpc": transformed_message["jsonrpc"],
            "id": transformed_message["id"],
            "result": response_dict
        }
        print(f"=====final response id: {final_response['id']}")

        return json.dumps(final_response).encode('utf-8')

    def jsonrpc_request(self, method: str, params={}, no_return=False, raw_response=False) -> dict:
        req_data = json.dumps({
            "jsonrpc": SharkdSession.JSONRPC_VERSION,
            "id": self.req_id,
            "method": method,
            "params": params
        }).encode()
        while True:
            response = self.communicate(req_data)
            if self.req_id in self.cached_response:
                res_data = self.cached_response[self.req_id]
            else:
                res_data = json.loads(response.decode("utf8", errors="ignore"))
            assert res_data["jsonrpc"] == SharkdSession.JSONRPC_VERSION, \
                "jsonrpc版本错误"
            if res_data["id"] != self.req_id:
                self.cached_response[res_data["id"]] = res_data
                continue
            self.req_id += 1
            if raw_response:
                return res_data
            if "error" in res_data:
                raise ValueError(res_data["error"]["message"])
            if no_return:
                assert res_data["result"] == {"status": "OK"}, \
                    "函数应返回status=OK"
            return res_data["result"]
