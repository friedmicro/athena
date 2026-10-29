# This is the lnk configuration; or more specifically
# configuration for shortcuts on Windows programs

from lib.config import read_json, write_json


class WindowsGamesConfig:
    manual_config_path = "./config/windows_games.json"

    def __init__(self, is_client=False):
        self.config = read_json(self.manual_config_path, is_client)
        self.is_client = is_client

    def fetch_exclude(self):
        return self.config["exclude"]

    def update_exclude(self, exclude):
        self.config["exclude"] = exclude
        write_json(self.manual_config_path, self.config, self.is_client)

    def fetch_open_steam_direct(self):
        return self.config["open_steam_direct"]

    def update_open_steam_direct(self, open_steam_direct):
        self.config["open_steam_direct"] = open_steam_direct
        write_json(self.manual_config_path, self.config, self.is_client)

    def fetch_steam_path(self):
        return self.config["steam_path"]

    def update_steam_path(self, steam_path):
        self.config["steam_path"] = steam_path
        write_json(self.manual_config_path, self.config, self.is_client)
