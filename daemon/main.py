import socket
import time

from lib.comm import process_socket_stream, respond_to_client
from lib.os import open_script, write_file
from lib.scanner import download_file

previous_unix_timestamp = 0
previous_operation = ""


def handle_bounce(operation):
    global previous_unix_timestamp
    global previous_operation
    unix_timestamp = time.time()
    if (
        unix_timestamp + 5 * 1000 > previous_unix_timestamp
        and previous_operation == operation
    ):
        time.sleep(5)
        print("Waiting 5 seconds due to fast command")
    previous_unix_timestamp = unix_timestamp
    previous_operation = operation


def process_operation(operation, params, conn):
    match operation:
        case "start":
            open_script("start")
        case "stop":
            open_script("stop")
        case "asset":
            print(params)
            write_file(params["path"], params["contents"], params["is_executable"])
        case "download":
            data = download_file(params["skip_steam"], params["skip_shortcut"])
            respond_to_client(conn, data, "download")
        case _:
            print("Not a valid option")
    if operation != "download":
        respond_to_client(conn)


PORT = 65432
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", PORT))
    s.listen()
    while True:
        received_data = b""
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            operation, params, _ = process_socket_stream(conn)
            handle_bounce(operation)
            print("Process operations")
            process_operation(operation, params, conn)
