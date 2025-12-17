import base64
import os
import platform
import shutil

from lib.config import read_json
from lib.os import get_os_delimiter, os_path_replace


def move_to_upload_location(files, file_type, mode="native"):
    file_type_location = "./assets/" + file_type
    asset_location = file_type_location + "/" + mode
    if not os.path.exists(file_type_location):
        os.mkdir(file_type_location)
    shutil.rmtree(asset_location, ignore_errors=True)
    os.mkdir(asset_location)
    for file in files:
        file_name = file.split(get_os_delimiter())[-1]
        shutil.copyfile(file, asset_location + "/" + file_name)


def find_files(path, file_type):
    path = os_path_replace(path)
    if not os.path.exists(path):
        return []
    files = os.listdir(path)
    filtered_files = []
    path_delimiter = get_os_delimiter()
    for file in files:
        if file_type in file:
            full_path = path + path_delimiter + file
            filtered_files.append(full_path)
    return filtered_files


def find_steam_acf_files(path):
    return find_files(path, ".acf")


def find_shortcut_files(path):
    return find_files(path, ".url") + find_files(path, ".lnk")


def move_steam_files_to_upload(path, mode="native"):
    files = find_files(path, ".acf")
    print(files)
    move_to_upload_location(files, "acf", mode)


def move_shortcut_files_to_upload(path):
    files = find_shortcut_files(path)
    move_to_upload_location(files, "native")


def move_to_upload(process_steam, process_shortcut):
    daemon_config = read_json("config.json")
    os_in_use = platform.system().lower()
    if not os.path.exists("assets"):
        os.mkdir("assets")
    if "linux" in os_in_use:
        if not process_steam:
            move_steam_files_to_upload(daemon_config["steam_apps_location_linux"])
            move_steam_files_to_upload(
                daemon_config["steam_apps_location_flatpak"], "flatpak"
            )
    elif "win" in os_in_use:
        if not process_steam:
            move_steam_files_to_upload(daemon_config["steam_apps_location_windows"])
        if not process_shortcut:
            move_shortcut_files_to_upload(daemon_config["shortcut_path"])
    else:
        print("Unsupported OS")
    shutil.make_archive("assets", "zip", "assets")


def download_file(process_steam, process_shortcut):
    move_to_upload(process_steam, process_shortcut)
    with open("assets.zip", "rb") as zip:
        zip_data = base64.b64encode(zip.read()).decode("utf-8")
    return zip_data
