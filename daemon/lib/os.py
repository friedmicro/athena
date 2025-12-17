import getpass
import os
import platform
import subprocess


def get_os_delimiter():
    os_in_use = platform.system().lower()
    path_delimiter = "/"
    if "win" in os_in_use:
        path_delimiter = "\\"
    return path_delimiter


def open_script(script_name):
    os_in_use = platform.system().lower()
    if "linux" in os_in_use:
        os_ext = ".sh"
        cmd_path = "/bin/bash"
    elif "win" in os_in_use:
        os_ext = ".bat"
        cmd_path = "C:\\WINDOWS\\system32\\cmd.exe"
    else:
        print("Unsupported OS")
        return
    trailing_slash = get_os_delimiter()
    script_directory = os.getcwd()
    script_full = f"{script_directory}{trailing_slash}{script_name}{os_ext}"
    subprocess.run(script_full, shell=True, executable=cmd_path)


def write_file(path, contents, is_executable):
    # Copy over game script, utilities, etc...assume full path
    # If $home$ or $desktop$ copy to the respective directory...this is OS agnostic, these do the same
    path = os_path_replace(path)
    # For Linux only, should the file be executable
    with open(path, "wb") as file:
        file.write(contents.encode("utf-8"))
    if is_executable:
        os.chmod(path, 0o775)


def os_path_replace(path):
    path = path.replace("~", "$home$")
    path = path.replace("$desktop$", "$home$")
    os_in_use = platform.system().lower()
    if "linux" in os_in_use:
        # Assume this is running under your user account on Linux
        username = getpass.getuser()
        path = path.replace("$home$", f"/home/{username}")
    elif "win" in os_in_use:
        # Window environment variables
        drive = os.environ["HOMEDRIVE"]
        home = os.environ["HOMEPATH"]
        path = path.replace("$home$", f"{drive}\\{home}\\Desktop")
        if not os.path.exists(path):
            path = path.replace("Desktop", "OneDrive\\Desktop")
        path = path.replace("/", "\\")
    return path
