import os

from scanners.emulators import parse_roms
from scanners.lib.config import write_json
from scanners.lnk import parse_lnk
from scanners.manual_remote import generate_manual
from scanners.steam import parse_acf


def parse_types(host, mode, file_type):
    match file_type:
        case "acf":
            return parse_acf(host, mode)
        case "lnk":
            return parse_lnk(host)
        case "manual":
            return generate_manual(host)
        case _:
            print("Type not defined, may be mistyped.")
            return {}


autogen_json = {}
for host in os.listdir("./data"):
    for file_type in os.listdir("./data/" + host):
        for mode in os.listdir("./data/" + host + "/" + file_type):
            autogen_json |= parse_types(host, mode, file_type)

autogen_json |= parse_roms()

write_json("./generators/out/autogen.json", autogen_json)
