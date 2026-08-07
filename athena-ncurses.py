import curses
import math
import os
import shutil
from functools import partial

from lib.config import read_json
from launcher.exec import setup_and_launch
from launcher.filter import clear_out_of_scope
from launcher.time_keep import athena_check, validate_whitelisted_days
from config_lib.install import create_initial_configs, InstallConfig


def render_table(app_data, stdscr):
    _, lines_max = shutil.get_terminal_size()
    row_line = app_data["row_line"]
    menu_topology = app_data["menu_topology"]

    stdscr.clear()

    for i, key in enumerate(menu_topology):
        page_offset = app_data["page"] * lines_max
        if i < page_offset:
            continue
        if i == lines_max - page_offset:
            break
        if row_line == i:
            stdscr.addstr(i - page_offset, 0, "--> " + key + " <--", curses.A_STANDOUT)
        else:
            stdscr.addstr(i - page_offset, 0, key)

    app_data["row_count"] = len(menu_topology)


def redraw_line(app_data, stdscr):
    _, lines_max = shutil.get_terminal_size()
    page_offset = app_data["page"] * lines_max
    row_line = app_data["row_line"]
    row_count = app_data["row_count"]
    if row_line - page_offset != 0:
        stdscr.move(row_line - 1 - page_offset, 0)
        stdscr.clrtoeol()
        top_line = list(app_data["menu_topology"].keys())[row_line - 1]
        stdscr.addstr(row_line - 1 - page_offset, 0, top_line)

    selected_line = list(app_data["menu_topology"].keys())[row_line]
    stdscr.addstr(
        row_line - page_offset, 0, "--> " + selected_line + " <--", curses.A_STANDOUT
    )

    if row_line != row_count - 1 and row_line != lines_max - 1:
        stdscr.move(row_line + 1 - page_offset, 0)
        stdscr.clrtoeol()
        bottom_line = list(app_data["menu_topology"].keys())[row_line + 1]
        stdscr.addstr(row_line + 1 - page_offset, 0, bottom_line)


def main(app_data, stdscr):
    render_table(app_data, stdscr)
    redraw_line(app_data, stdscr)

    while True:
        row_line = app_data["row_line"]
        previous_page = app_data["page"]

        curses.curs_set(0)

        user_input = stdscr.get_wch()
        _, lines_max = shutil.get_terminal_size()

        if user_input == curses.KEY_DOWN:
            row_line += 1
            app_data["row_line"] = row_line
            app_data["page"] = math.floor(row_line / lines_max)
        elif user_input == curses.KEY_UP:
            row_line -= 1
            app_data["row_line"] = row_line
            app_data["page"] = math.floor(row_line / lines_max)
        # This is the escape key
        elif user_input == "\x1b":
            app_data["menu_topology"] = app_data["prior_menu_topology"]
            render_table(app_data, stdscr)
            continue
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
                continue

        # User scrolled past in either direction, reset them to the first item
        if app_data["row_line"] < 0 or app_data["row_line"] >= len(
            app_data["menu_topology"]
        ):
            app_data["row_line"] = 0
            app_data["page"] = 0
            render_table(app_data, stdscr)
            redraw_line(app_data, stdscr)
            continue

        if previous_page != app_data["page"]:
            render_table(app_data, stdscr)
        else:
            redraw_line(app_data, stdscr)

        if app_data["should_exit"]:
            break

if __name__ == '__main__':
    athena_check()

    create_initial_configs(InstallConfig())

    menu_topology = read_json("config.json")
    menu_topology = clear_out_of_scope(menu_topology)

    app_data = {
        "page": 0,
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
