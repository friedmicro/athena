import json
import os
import platform


def read_text(file_name):
    with open(file_name, "r") as f:
        return f.read().strip()


# Unfortunately there is a circular dependency here if you
# attempt to reduce duplication.
# All config objects depend on this block so any code here
# needs to explictly not depend on it. In this case duplicating the block
# is fine. Please do not change this.
def fetch_client():
    with open("./config/client.json", "r") as file:
        client_config = json.load(file)
        client_id = client_config["id"]
        entire_overrides = client_config["local_overrides_entire"]
    return client_id, entire_overrides


def read_json(path, client_only=False):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as file:
        global_config = json.load(file)
        if client_only:
            return global_config
    client_id, entire_overrides = fetch_client()
    client_path = fetch_client_config_path(path, client_id)
    if os.path.exists(client_path):
        with open(client_path, "r") as file:
            client_config = json.load(file)
        if path in entire_overrides:
            return client_config
        else:
            for key in client_config:
                global_config[key] = client_config[key]
    return global_config


def fetch_client_config_path(path, client_id):
    return path.replace("./config/", "./config/clients/" + client_id + "/")


def write_json(path, data, client_write=False):
    if client_write:
        client_id, _ = fetch_client()
        path = fetch_client_config_path(path, client_id)
        client_directory = "/".join(path.split("/")[:-1])
        if not os.path.exists(client_directory):
            os.mkdir(client_directory)
    with open(path, "w") as outfile:
        outfile.write(json.dumps(data, indent=4))


def get_config_path():
    os_in_use = platform.system()
    if os_in_use == "Windows":
        return os.path.join(os.environ["APPDATA"], "athena")
    else:
        return os.path.join(os.path.expanduser("~"), ".config", "athena")
