from lib.config import read_json, write_json


class RegisteredEmulator(dict):
    def __init__(self, name, config_map):
        self.name = name
        self.paths = str(config_map["paths"][name])
        self.scan = config_map["scan"][name]
        self.extensions = config_map["extensions"][name]
        self.is_single_file = config_map["is_single_file"][name]
        self.truncate_sequence = config_map["truncate_sequence"][name]
        self.exec = config_map["exec"][name]
        dictionary_map = {
            "name": self.name,
            "paths": self.paths,
            "scan": self.scan,
            "extensions": self.extensions,
            "is_single_file": self.is_single_file,
            "truncate_sequence": self.truncate_sequence,
            "exec": self.exec,
        }
        super().__init__(self, **dictionary_map)


class EmulatorConfig:
    manual_config_path = "./config/emulators.json"

    def __init__(self, is_client=False):
        self.config_data = read_json(self.manual_config_path, is_client)
        self.emulators = {}
        for emulator_name in self.config_data["registered_emulators"]:
            self.emulators[emulator_name] = RegisteredEmulator(
                emulator_name, self.config_data
            )
        self.selected = self.config_data["selected"]
        self.remapping = self.config_data["remapping"]
        self.is_client = is_client

    def write_config(self):
        write_json(self.manual_config_path, self.config_data, self.is_client)

    def fetch_remapping(self):
        return self.config_data["remapping"]

    def update_remapping(self, remapping):
        self.config_data["remapping"] = remapping
        self.write_config()

    def fetch_selected(self):
        return self.config_data["selected"]

    def update_selected(self, selected):
        self.config_data["selected"] = selected
        self.write_config()

    def fetch_emulators(self) -> dict[str, RegisteredEmulator]:
        return self.emulators

    def fetch_emulator(self, name) -> RegisteredEmulator:
        return self.emulators[name]

    def update_emulator(self, name, emulator_config):
        self.emulators[name] = RegisteredEmulator(name, emulator_config)
        self.config_data["paths"][name] = emulator_config["paths"]
        self.config_data["scan"][name] = emulator_config["scan"]
        self.config_data["extensions"][name] = emulator_config["extensions"]
        self.config_data["is_single_file"][name] = emulator_config["is_single_file"]
        self.config_data["truncate_sequence"][name] = emulator_config[
            "truncate_sequence"
        ]
        self.config_data["exec"][name] = emulator_config["exec"]
        self.write_config()

    def add_emulator(self, name):
        self.config_data["registered_emulators"].append(name)
        self.emulators[name] = {
            "paths": [],
            "scan": [],
            "extensions": [],
            "is_single_file": False,
            "truncate_sequence": False,
            "exec": "",
        }
        self.config_data["paths"][name] = self.emulators[name]["paths"]
        self.config_data["scan"][name] = self.emulators[name]["scan"]
        self.config_data["extensions"][name] = self.emulators[name]["extensions"]
        self.config_data["is_single_file"][name] = self.emulators[name][
            "is_single_file"
        ]
        self.config_data["truncate_sequence"][name] = self.emulators[name][
            "truncate_sequence"
        ]
        self.config_data["exec"][name] = self.emulators[name]["exec"]
        self.write_config()
