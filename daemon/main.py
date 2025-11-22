import getpass
import json
import os
import platform
import socket
import subprocess
import time

from cryptography.fernet import Fernet

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


def open_script(script_name):
    os_in_use = platform.system().lower()
    if "linux" in os_in_use:
        os_ext = ".sh"
    elif "win" in os_in_use:
        os_ext = ".bat"
    else:
        print("Unsupported OS")
        return
    script_full = f"./{script_name}{os_ext}"
    subprocess.run(script_full, shell=True)


def write_file(params):
    # Copy over game script, utilities, etc...assume full path
    path = params["path"]
    # If $home$ or $desktop$ copy to the respective directory...this is OS agnostic, these do the same
    path = path.replace("$desktop$", "$home$")
    os_in_use = platform.system().lower()
    if "linux" in os_in_use:
        # Assume this is running under your user account on Linux
        username = getpass.getuser()
        path = path.replace("$home$", f"/home/{username}")
    elif "win" in os_in_use:
        # Window environment variables
        drive = os.environ["HOMEDRIVE"]
        home = os.environ["HOMEPATH"]
        path = path.replace("$home$", f"{drive}\\{home}\\Desktop")
        path = path.replace("/", "\\")
    print(path)
    contents = params["contents"]
    # For Linux only, should the file be executable
    with open(path, "w") as file:
        file.write(contents)
    is_executable = params["is_executable"]
    if is_executable:
        os.chmod(path, 0o775)


def process_operation(operation, params):
    match operation:
        case "start":
            open_script("start")
        case "stop":
            open_script("stop")
        case "asset":
            write_file(params)
        case _:
            print("Not a valid option")


def process_message(data):
    decoded_message = data.decode("utf-8")
    crypto_key = Fernet(auth())
    decrypted_message = json.loads(crypto_key.decrypt(decoded_message))
    operation = decrypted_message["operation"]
    params = decrypted_message["params"]
    handle_bounce(operation)
    return operation, params


def auth():
    credentials_file = "initial_config.bin"
    if not os.path.exists(credentials_file):
        encrypt_pass = Fernet.generate_key()
        with open(credentials_file, "wb") as file_object:
            file_object.write(encrypt_pass)
    else:
        with open(credentials_file, "rb") as file_object:
            encrypt_pass = file_object.read()
    return encrypt_pass


PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", PORT))
    s.listen()
    while True:
        received_data = b""
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    conn.close()
                    break
                received_data += data
                operation, params = process_message(received_data)
                process_operation(operation, params)
                conn.sendall(b"Server received your message!")
