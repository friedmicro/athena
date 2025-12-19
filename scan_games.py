import base64
import os
import platform
import shutil
import subprocess
import zipfile

from daemon.lib.comm import request_from_daemon
from daemon.lib.scanner import find_steam_acf_files
from scanners.emulators import parse_roms
from scanners.lib.config import read_json, write_json
from scanners.lnk import parse_lnk
from scanners.manual_remote import generate_manual
from scanners.steam import parse_acf
from scanners.waydroid import generate_waydroid
from scanners.web import generate_web_pages


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


os_in_use = platform.system().lower()
steam_locations = read_json("./config/steam.json")[os_in_use]["locations"]

local_path = "./data/local"
shutil.rmtree(local_path, ignore_errors=True)
os.mkdir(local_path)
os.mkdir(local_path + "/acf")
acfs = []
for location in steam_locations:
    location_path = location["path"]
    acfs += find_steam_acf_files(location_path)
    os.mkdir(local_path + "/acf/" + location["mode"])
    for acf in acfs:
        manifest_file = acf.split("/")[-1]
        shutil.copyfile(
            acf, local_path + "/acf/" + location["mode"] + "/" + manifest_file
        )


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

autogen_json = {}
for host in os.listdir("./data"):
    for file_type in os.listdir("./data/" + host):
        for mode in os.listdir("./data/" + host + "/" + file_type):
            autogen_json |= parse_types(host, mode, file_type)

autogen_json |= parse_roms()
autogen_json |= generate_web_pages()
autogen_json |= generate_waydroid()

write_json("./generators/out/autogen.json", autogen_json)
