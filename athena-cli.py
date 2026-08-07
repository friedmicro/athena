# CLI for users who want to use a command line interface
# also used by GUI tools.
import subprocess
import sys

from config_cli.config import config
from config_lib.client import GeneratorConfig
from config_lib.install import InstallConfig, create_initial_configs
from daemon.lib.comm import auth
from launcher.exec import setup_and_launch
from launcher.time_keep import athena_check, validate_whitelisted_days
from lib.config import read_json
from remote.manage import force_stop_remote, remove_tracking

all_programs = []


def flatten_config(config):
    for entry in config:
        if "script" not in config[entry]:
            flatten_config(config[entry])
        else:
            config[entry]["name"] = entry
            all_programs.append(config[entry])
    return all_programs


def process_config_data():
    config = read_json("./config.json")
    return flatten_config(config)


def find_program_args(all_programs, program_to_call):
    for program in all_programs:
        if program["name"] == program_to_call:
            return program
    return None


def start_program(program_to_call):
    all_programs = process_config_data()
    program_args = find_program_args(all_programs, program_to_call)

    is_logging_time = False
    if program_args is None:
        sys.exit(42)
    if "time_limit" in program_args:
        if program_args["time_limit"]:
            validate_whitelisted_days()
            is_logging_time = True
    setup_and_launch(is_logging_time, program_args)


def process_user_input():
    launch_option = sys.argv[1]
    if launch_option == "start":
        program_to_call = sys.argv[2]
        start_program(program_to_call)
    elif launch_option == "remote":
        remote_command = sys.argv[2]
        host_to_control = sys.argv[3]
        if remote_command == "stop":
            force_stop_remote(host_to_control)
        elif remote_command == "remove_tracking":
            remove_tracking(host_to_control)
        else:
            sys.exit(42)
    elif launch_option == "config":
        config(sys.argv[2:])
    elif launch_option == "gen":
        generator_config = GeneratorConfig()
        subprocess.run(generator_config.generator_path)
    elif launch_option == "auth":
        auth()
    else:
        program_to_call = sys.argv[1]
        start_program(program_to_call)

if __name__ == '__main__':
    athena_check()
    create_initial_configs(InstallConfig())
    process_user_input()
