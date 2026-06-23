from lib.config import read_json, write_json


class AccessibilityConfig:
    manual_config_path = "./config/accessibility.json"

    def __init__(self, is_client=False) -> None:
        self.is_client = is_client
        self.config_data = read_json(self.manual_config_path, is_client)
        pass

    def load_whitelisted(self):
        return self.config_data["whitelisted_entries"]

    def should_generate(self):
        return self.config_data["generate_config"]

    def write_config(self, new_config_data):
        self.config_data = new_config_data
        write_json(self.manual_config_path, new_config_data)
