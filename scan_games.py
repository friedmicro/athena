import base64
import os
import platform
import shutil
import subprocess
import zipfile

from config_lib.remote import RemoteConfig
from config_lib.steam import SteamConfig
from daemon.lib.comm import request_from_daemon
from daemon.lib.scanner import find_steam_acf_files
from launcher.launch_preferences import merge_based_on_props
from lib.accessibility import generate_accessible_file
from lib.config import write_json
from lib.os import mkdirp
from scanners.emulators import parse_roms
from scanners.lnk import parse_lnk
from scanners.manual import generate_manual_local, generate_manual_remote
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
            return generate_manual_remote(host)
        case _:
            print("Type not defined, may be mistyped.")
            return {}


os_in_use = platform.system().lower()
steam_locations = SteamConfig().fetch_host(os_in_use).locations

local_path = "./data/local"
shutil.rmtree(local_path, ignore_errors=True)
os.mkdir(local_path)
os.mkdir(local_path + "/acf")
for location in steam_locations:
    acfs = []
    location_path = location.path
    acfs += find_steam_acf_files(location_path)
    os.mkdir(local_path + "/acf/" + location.mode)
    for acf in acfs:
        manifest_file = acf.split("/")[-1]
        shutil.copyfile(acf, local_path + "/acf/" + location.mode + "/" + manifest_file)


remote_config = RemoteConfig()
request_body = {
    "operation": "download",
    "params": remote_config.fetch_scan_options(),
}

remote_hosts = remote_config.fetch_hosts()
for host in remote_config.fetch_remotes_to_load():
    remote_host = remote_hosts[host]
    host_name = remote_host.ip
    if "start_script" in remote_host:
        subprocess.run([remote_host.start_script])
    if remote_host.athena_installed:
        data = str(request_from_daemon(remote_host.ip, request_body))
        with open("assets.zip", "wb") as file:
            file.write(base64.b64decode(data))
        with zipfile.ZipFile("assets.zip", "r") as zip:
            target_path = "./data/" + host
            shutil.rmtree(target_path)
            zip.extractall(target_path)
    else:
        mkdirp("./data/" + host)
    if "manual" in remote_host:
        manual_config = remote_host.manual
        manual_path = "./data/" + host + "/manual"
        mkdirp(manual_path)
        write_json(manual_path + "/config.json", manual_config)
    if "stop_script" in remote_host:
        subprocess.run([remote_host.stop_script])

autogen_json = {}
for host in os.listdir("./data"):
    for file_type in os.listdir("./data/" + host):
        for mode in os.listdir("./data/" + host + "/" + file_type):
            parsed_json = parse_types(host, mode, file_type)
            autogen_json = merge_based_on_props(autogen_json, parsed_json)

autogen_json |= generate_manual_local()
autogen_json |= parse_roms()
autogen_json |= generate_web_pages()
autogen_json |= generate_waydroid()

autogen_json = generate_accessible_file(autogen_json)

write_json("./generators/out/autogen.json", autogen_json)
