import json
import socket

from cryptography.fernet import Fernet

HOST = "192.168.1.8"  # Change IP...this is just test code
PORT = 65432

with open("initial_config.bin", "rb") as file_object:
    encrypt_pass = file_object.read()

crypto_key = Fernet(encrypt_pass)
while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        message_request = {
            "operation": "asset",
            "params": {
                "path": "$home$/test-file",
                "contents": "echo hello",
                "is_executable": True,
            },
        }
        message_body = json.dumps(message_request).encode()
        encrypted_message = crypto_key.encrypt(message_body)
        s.sendall(encrypted_message)
        data = s.recv(1024)
        print(f"Received from server: {data.decode('utf-8')}")
        s.close()
