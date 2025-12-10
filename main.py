import calendar
import curses
import datetime
import json
import multiprocessing
import os
import socket
import subprocess
import sys
import time
from functools import partial

from cryptography.fernet import Fernet

from scanners.lib.config import read_json, read_text


def render_table(app_data, stdscr):
    row_line = app_data["row_line"]
    menu_topology = app_data["menu_topology"]

    stdscr.clear()

    for i, key in enumerate(menu_topology):
        if row_line == i:
            stdscr.addstr(i, 0, "--> " + key + " <--", curses.A_STANDOUT)
        else:
            stdscr.addstr(i, 0, key)

    app_data["row_count"] = len(menu_topology)


def redraw_line(app_data, stdscr):
    row_line = app_data["row_line"]
    row_count = app_data["row_count"]
    if row_line != 0:
        stdscr.move(row_line - 1, 0)
        stdscr.clrtoeol()
        top_line = list(app_data["menu_topology"].keys())[row_line - 1]
        stdscr.addstr(row_line - 1, 0, top_line)

    selected_line = list(app_data["menu_topology"].keys())[row_line]
    stdscr.addstr(row_line, 0, "--> " + selected_line + " <--", curses.A_STANDOUT)

    if row_line != row_count - 1:
        stdscr.move(row_line + 1, 0)
        stdscr.clrtoeol()
        bottom_line = list(app_data["menu_topology"].keys())[row_line + 1]
        stdscr.addstr(row_line + 1, 0, bottom_line)


def main(app_data, stdscr):
    row_line = app_data["row_line"]
    row_count = app_data["row_count"]

    render_table(app_data, stdscr)

    while True:
        row_count = app_data["row_count"]

        curses.curs_set(0)

        redraw_line(app_data, stdscr)

        user_input = stdscr.get_wch()

        if user_input == curses.KEY_DOWN:
            row_line += 1
            if row_line >= row_count:
                row_line = row_count - 1
        elif user_input == curses.KEY_UP:
            row_line -= 1
            if row_line < 0:
                row_line = 0
        # This is the escape key
        elif user_input == "\x1b":
            app_data["menu_topology"] = app_data["prior_menu_topology"]
            render_table(app_data, stdscr)
        elif user_input == "q":
            app_data["should_exit"] = True
        # 10 is enter if not a number pad
        elif user_input == "\n":
            app_data["menu_topology"] = list(app_data["menu_topology"].values())[
                row_line
            ]
            app_data["row_line"] = 0
            row_line = 0
            if "script" in app_data["menu_topology"]:
                break
            else:
                render_table(app_data, stdscr)

        app_data["row_line"] = row_line

        if app_data["should_exit"]:
            break


config_file_handler = open("time_config.json")
time_configuration = json.load(config_file_handler)
config_file_handler.close()

time_log_handler = open("time.json")
time_ledger = json.load(time_log_handler)
time_log_handler.close()


def validate_whitelisted_days():
    no_time_to_play = time_configuration["no_time_to_play"]
    today = datetime.datetime.today()
    day_of_week = today.weekday()
    time_saver_trigger = time_configuration["time_saver_trigger"]
    if os.path.exists(time_saver_trigger):
        whitelisted_days = time_configuration["whitelisted_days"]
        day_is_not_allowed = True
        for day in whitelisted_days:
            if calendar.day_name[day_of_week] == day:
                day_is_not_allowed = False

        if day_is_not_allowed:
            print(no_time_to_play)
            sys.exit(42)


def time_counter_loop(args):
    current_time = args
    first_warning = False
    final_warning = False
    while True:
        current_time += 1
        time.sleep(1)
        if (
            current_time > time_configuration["first_warning_time"]
            and first_warning == False
        ):
            first_warning_hook = time_configuration["first_warning_hook"]
            first_warning = True
            subprocess.call(first_warning_hook, shell=True)
        if (
            current_time > time_configuration["final_warning_time"]
            and final_warning == False
        ):
            final_warning_hook = time_configuration["final_warning_hook"]
            final_warning = True
            subprocess.call(final_warning_hook, shell=True)


def send_daemon_message(host, message_request):
    PORT = 65432

    with open("initial_config.bin", "rb") as file_object:
        encrypt_pass = file_object.read()

    crypto_key = Fernet(encrypt_pass)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, PORT))
        message_body = json.dumps(message_request).encode()
        encrypted_message = crypto_key.encrypt(message_body)
        s.sendall(encrypted_message)
        data = s.recv(1024)
        print(f"Received from server: {data.decode('utf-8')}")
        s.close()


def send_stop(host):
    send_daemon_message(host, {"operation": "stop", "params": ""})


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


def execute_program_with_time_logging(selected_item):
    time_saver_trigger = time_configuration["time_saver_trigger"]

    if os.path.exists(time_saver_trigger):
        week_number = int(datetime.datetime.today().strftime("%V"))
        if time_ledger["week_number"] != week_number:
            time_ledger["week_number"] = week_number
            time_ledger["ledger"] = {}
        today = datetime.datetime.today()
        day_of_week = str(today.weekday())
        if day_of_week not in time_ledger["ledger"]:
            time_ledger["ledger"][day_of_week] = {}

        start_time = int(time.time())

        current_time_total = 0
        for time_record in time_ledger["ledger"][day_of_week]:
            current_time_total += time_ledger["ledger"][day_of_week][time_record] - int(
                time_record
            )

        print(current_time_total)

        if current_time_total >= time_configuration["first_warning_time"]:
            print(time_configuration["time_limit_reached"])
            return

        time_ledger["ledger"][day_of_week][start_time] = None

        thread = multiprocessing.Process(
            target=time_counter_loop, args=(current_time_total,)
        )
        thread.start()

    launch_program(selected_item)

    if os.path.exists(time_saver_trigger):
        end_time = int(time.time())
        time_ledger["ledger"][day_of_week][start_time] = end_time

        thread.terminate()

        with open("time.json", "w") as file_handler:
            json.dump(time_ledger, file_handler, indent=4)
        file_handler.close()


def launch_program(selected_item):
    if selected_item["script"] != "":
        subprocess.run([selected_item["script"]])
    if "emulator" in selected_item:
        emulator_config = read_json("./config/emulators.json")
        emulator_exec = emulator_config[selected_item["emulator"]]
        asset = selected_item["asset"]
        emulator_exec = emulator_exec.replace("{rom_path}", asset)
        subprocess.run([emulator_exec], shell=True)
    elif "asset" in selected_item:
        send_start(selected_item["ip"])
        send_asset(selected_item["ip"], selected_item["asset"], selected_item["os"])
        remote_config = read_json("./config/remote.json")
        remote_type = selected_item["remote_client_type"]
        if remote_type == "moonlight":
            moonlight_command = (
                remote_config["defaults"]["moonlight_client_path"]
                + " stream "
                + selected_item["moonlight_machine"]
                + " "
                + selected_item["moonlight_app"]
            )
            subprocess.run([moonlight_command], shell=True)
        send_stop(selected_item["ip"])


def setup_and_launch(is_logging_time, selected_item):
    if "start_script" in selected_item and selected_item["start_script"] != "":
        subprocess.run([selected_item["start_script"]], shell=True)
    if is_logging_time:
        execute_program_with_time_logging(selected_item)
    else:
        launch_program(selected_item)
    if "stop_script" in selected_item and selected_item["stop_script"] != "":
        subprocess.run([selected_item["stop_script"]], shell=True)


with open("config.json", "r") as file:
    menu_topology = json.load(file)

app_data = {
    "row_line": 0,
    "should_exit": False,
    "row_count": len(menu_topology),
    "menu_topology": menu_topology,
    "prior_menu_topology": menu_topology,
}

# Some terminals set a very high delay for escape, overwrite this
os.environ.setdefault("ESCDELAY", str(5))
# Open the ncurses interface and selection
# appdata menu_topology key will mutate for a command to run
curses.wrapper(partial(main, app_data))
# If we should not launching a program with a time restriction exit the program
is_logging_time = False
if "time_limit" in app_data["menu_topology"]:
    if app_data["menu_topology"]["time_limit"] == True:
        # We assume the time_config.json file is present if you are doing time options
        # Seeing as otherwise it will crash\not do anything
        validate_whitelisted_days()
        is_logging_time = True
selected_item = app_data["menu_topology"]
setup_and_launch(is_logging_time, selected_item)
