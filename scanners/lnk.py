import os

import LnkParse3

from scanners.lib.config import read_json
from scanners.lib.remote import form_remote_props

windows_games = read_json("./config/windows_games.json")
remote_config = read_json("./config/remote.json")
windows_exclusions = windows_games["exclude"]
open_steam_direct = windows_games["open_steam_direct"]


# Because Steam doesn't use lnk files.
def steam_template(program_name, url_destination):
    steam_path = windows_games["steam_path"]
    if program_name in open_steam_direct:
        return f'"{windows_games["steam_path"]}"'
    return f"""\"{steam_path}\" {url_destination}
""".format(steam_path=steam_path, url_destination=url_destination)


def lnk_template(program_name, target, arguments):
    return """cd \"{program_name}\"
\"{target}\" {arguments}
""".format(program_name=program_name, target=target, arguments=arguments)


def write_asset(bat_name, asset_contents):
    file_path = "./scripts/assets/" + bat_name
    f = open(file_path, "w")
    f.write(asset_contents)
    f.close()
    return file_path


def parse_lnk(host):
    games_json = {}
    directory_path = "./data/" + host + "/lnk/native"
    entries = os.listdir(directory_path)
    for file_name in entries:
        program_name = file_name.split(".")[0]
        asset_name = program_name + ".bat"
        if program_name in windows_exclusions:
            continue
        if ".url" in file_name or ".lnk" in file_name:
            games_json[program_name] = {}
        else:
            continue
        if ".url" in file_name:
            with open(f"{directory_path}/{file_name}", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if "URL" in line:
                        if "steam" not in line:
                            continue
                        url_destination = line.split("URL=")[1].strip()
                        contents = steam_template(program_name, url_destination)
                        games_json[program_name]["asset"] = write_asset(
                            asset_name, contents
                        )
        elif ".lnk" in file_name:
            lnk_file = open(f"{directory_path}/{file_name}", "rb")
            lnk = LnkParse3.lnk_file(lnk_file)
            working_directory = lnk.get_json()["data"]["working_directory"]
            target = lnk.get_json()["link_info"]["local_base_path"]
            arguments = ""
            if "command_line_arguments" in lnk.get_json()["data"]:
                arguments = lnk.get_json()["data"]["command_line_arguments"]
            contents = lnk_template(working_directory, target, arguments)
            games_json[program_name]["asset"] = write_asset(asset_name, contents)
        form_remote_props(games_json, program_name, host)

    return games_json
