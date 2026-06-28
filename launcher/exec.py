import datetime
import math
import multiprocessing
import os
import platform
import subprocess
import time

from config_lib.athena import AthenaConfigItem
from config_lib.emulators import EmulatorConfig
from config_lib.web import WebConfig
from launcher.time_keep import is_item_time_whitelisted, time_counter_loop
from lib.config import read_json, write_json
from remote.exec import daemon_start, daemon_stop, execute_client_remote
from remote.manage import start_remote, stop_remote

time_configuration = read_json("./config/time_config.json")
time_ledger = read_json("time.json")


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

        minutes = math.floor(current_time_total / 60)
        display_minutes = minutes % 60
        seconds = current_time_total - (minutes * 60)
        hours = math.floor(minutes / 60)
        print(str(hours) + ":" + str(display_minutes) + ":" + str(seconds))

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

        write_json("time.json", time_ledger)


def launch_program(selected_item: AthenaConfigItem):
    if selected_item.has_script_override():
        subprocess.run([selected_item.script])
    elif selected_item.is_emulator():
        emulator_config = EmulatorConfig().fetch_emulator(selected_item.emulator)
        asset = selected_item.asset
        emulator_exec = emulator_config.exec.replace("{rom_path}", asset)
        subprocess.run([emulator_exec], shell=True)
    elif selected_item.is_layer():
        if selected_item.is_waydroid():
            subprocess.run(
                ["waydroid app launch " + selected_item.asset + " &"], shell=True
            )
    elif selected_item.is_web():
        web_config = WebConfig()
        os_in_use = platform.system().lower()
        if web_config.fetch_close_existing():
            kill_exec = "killall " + web_config.fetch_browser()
            if "win" in os_in_use:
                browser_binary = web_config.fetch_browser().split("/")[-1]
                kill_exec = "taskkill /IM " + browser_binary
            subprocess.run([kill_exec], shell=True)
            # Give the process time to gracefully close
            time.sleep(2)
        browser_exec = web_config.fetch_browser() + " "
        if web_config.fetch_kiosk():
            browser_exec += "--kiosk "
        browser_exec += selected_item.web
        subprocess.run([browser_exec], shell=True)
    elif selected_item.is_remote():
        execute_client_remote(selected_item)


def setup_and_launch(is_logging_time, selected_item):
    selected_item = AthenaConfigItem(selected_item)
    start_remote(selected_item)
    if is_logging_time:
        if is_item_time_whitelisted(selected_item):
            launch_program(selected_item)
        else:
            execute_program_with_time_logging(selected_item)
    else:
        launch_program(selected_item)
    stop_remote(selected_item)


def headless_start(selected_item):
    selected_item = AthenaConfigItem(selected_item)
    start_remote(selected_item)
    daemon_start(selected_item)


def headless_stop(selected_item):
    selected_item = AthenaConfigItem(selected_item)
    stop_remote(selected_item)
    daemon_stop(selected_item)
