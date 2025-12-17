import base64
import os
import shutil
import subprocess
import zipfile

from daemon.lib.comm import request_from_daemon
from scanners.emulators import parse_roms
from scanners.lib.config import read_json, write_json
from scanners.lnk import parse_lnk
from scanners.manual_remote import generate_manual
from scanners.steam import parse_acf
from scanners.web import generate_web_pages

remote_config = read_json("./config/remote.json")
skip_steam = remote_config["scan_options"]["skip_steam"]
skip_shortcut = remote_config["scan_options"]["skip_shortcut"]

request_body = {
    "operation": "download",
    "params": {"skip_steam": skip_steam, "skip_shortcut": skip_shortcut},
}

for host in remote_config["remotes_to_load"]:
    host_name = remote_config[host]["ip"]
    if "start_script" in remote_config[host]:
        subprocess.run([remote_config[host]["start_script"]])
    data = str(request_from_daemon("lair.friedmicro-lab.org", request_body))
    with open("assets.zip", "wb") as file:
        file.write(base64.b64decode(data))
    with zipfile.ZipFile("assets.zip", "r") as zip:
        target_path = "./data/" + host
        shutil.rmtree(target_path)
        zip.extractall(target_path)
    if "stop_script" in remote_config[host]:
        subprocess.run([remote_config[host]["stop_script"]])


def parse_types(host, mode, file_type):
    match file_type:
        case "acf":
            return parse_acf(host, mode)
        case "lnk":
            return parse_lnk(host)
        case "manual":
            return generate_manual(host)
        case _:
            print("Type not defined, may be mistyped.")
            return {}


autogen_json = {}
for host in os.listdir("./data"):
    for file_type in os.listdir("./data/" + host):
        for mode in os.listdir("./data/" + host + "/" + file_type):
            autogen_json |= parse_types(host, mode, file_type)

autogen_json |= parse_roms()
autogen_json |= generate_web_pages()

write_json("./generators/out/autogen.json", autogen_json)
