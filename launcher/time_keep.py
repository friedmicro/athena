import calendar
import datetime
import os
import subprocess
import sys
import time

from launcher.lib.config import read_json

time_configuration = read_json("time_config.json")


def is_item_time_whitelisted(selected_item):
    now = datetime.datetime.now()
    schedule = selected_item["time_schedule"]
    schedule_day = schedule["day"]
    schedule_start_hour = schedule["start_time"].split(":")[0]
    schedule_start_minute = schedule["start_time"].split(":")[1]
    schedule_end_hour = schedule["end_time"].split(":")[0]
    schedule_end_minute = schedule["end_time"].split(":")[1]
    if schedule_day == now.strftime("%A"):
        if schedule_start_hour <= now.hour and schedule_end_hour >= now.hour:
            if (
                schedule_start_minute <= now.minute
                and schedule_end_minute >= now.minute
            ):
                return True

    return False


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
