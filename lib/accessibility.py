from config_lib.accessibility import AccessibilityConfig


def generate_accessible_file(json_config):
    clean_config = {}
    access_config = AccessibilityConfig()
    whitelisted = access_config.load_whitelisted()
    if access_config.should_generate():
        for key, value in json_config.items():
            if key in whitelisted:
                clean_config[key] = value
        return clean_config
    return json_config
