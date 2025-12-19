from scanners.lib.config import read_json


def generate_waydroid():
    output_json = {}
    manual_config_path = "./config/android.json"
    games = read_json(manual_config_path)
    for game in games:
        output_json[game] = {"layer": "waydroid", "script": "", "asset": games[game]}
    return output_json
