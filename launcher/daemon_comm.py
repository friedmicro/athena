from daemon.lib.comm import send_daemon_message
from launcher.lib.config import read_text


def send_stop(host):
    send_daemon_message(host, {"operation": "stop", "params": ""}, 10 * 60)


def send_start(host):
    send_daemon_message(host, {"operation": "start", "params": ""})


def send_asset(host, asset_path, remote_os):
    asset_contents = read_text(asset_path)
    game_name = "game"
    if remote_os == "linux":
        game_name += ".sh"
    elif remote_os == "windows":
        game_name += ".bat"
    message_request = {
        "operation": "asset",
        "params": {
            "path": "$home$/" + game_name,
            "contents": asset_contents,
            "is_executable": True,
        },
    }
    send_daemon_message(host, message_request)
