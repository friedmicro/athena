import json
import os
import socket

from cryptography.fernet import Fernet

end_of_stream_sequence = "%$FIN$%"
end_character_length = len(end_of_stream_sequence)


def encode_message(message_request):
    with open("initial_config.bin", "rb") as file_object:
        encrypt_pass = file_object.read()

    crypto_key = Fernet(encrypt_pass)
    message_body = json.dumps(message_request).encode()
    encrypted_message = crypto_key.encrypt(message_body)
    return encrypted_message


def create_daemon_conn(host, timeout=None):
    PORT = 65432

    with open("initial_config.bin", "rb") as file_object:
        encrypt_pass = file_object.read()

    crypto_key = Fernet(encrypt_pass)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, PORT))
    s.settimeout(timeout)
    return s, crypto_key


def create_daemon_conn_and_message(host, message_request, timeout=None):
    conn, crypto_key = create_daemon_conn(host, timeout)
    send_on_conn(conn, crypto_key, message_request)
    return conn


def send_on_conn(conn, crypto_key, message_request):
    message_body = json.dumps(message_request).encode()
    encrypted_message = crypto_key.encrypt(message_body)
    encrypted_message = encrypted_message.decode("utf-8") + end_of_stream_sequence
    encrypted_message = encrypted_message.encode()
    conn.sendall(encrypted_message)


def auth():
    credentials_file = "initial_config.bin"
    if not os.path.exists(credentials_file):
        encrypt_pass = Fernet.generate_key()
        with open(credentials_file, "wb") as file_object:
            file_object.write(encrypt_pass)
    else:
        with open(credentials_file, "r") as file_object:
            encrypt_pass = file_object.read()
    return encrypt_pass


def decode_message(data):
    decoded_message = data.decode("utf-8")
    crypto_key = Fernet(auth())
    decrypted_message = json.loads(crypto_key.decrypt(decoded_message))
    operation = decrypted_message["operation"]
    params = None
    data = None
    if "params" in decrypted_message:
        params = decrypted_message["params"]
    if "data" in decrypted_message:
        data = decrypted_message["data"]
    return operation, params, data


def process_socket_stream(s):
    received_data = b""
    while True:
        data = s.recv(1024)
        if not data:
            break
        if data.decode("utf-8")[-end_character_length:] == end_of_stream_sequence:
            received_data += data[:-end_character_length]
            break
        received_data += data
    return decode_message(received_data)


def request_from_daemon(host, message_request, timeout=None):
    conn, crypto_key = create_daemon_conn(host, timeout)
    send_on_conn(conn, crypto_key, message_request)
    (
        _,
        _,
        data,
    ) = process_socket_stream(conn)
    conn.close()
    return data


def send_daemon_message(host, message_request, timeout=None):
    s = create_daemon_conn_and_message(host, message_request, timeout)
    s.close()


def respond_to_client(conn, data="", operation="no_data"):
    message = {"data": data, "operation": operation}
    message_to_send = encode_message(message)
    conn.sendall(message_to_send)
    conn.close()
