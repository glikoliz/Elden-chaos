from pymem import Pymem
import json
from importlib import import_module
from random import choices


def get_worldchrman(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x05....\x48\x85\xC0\x74\x0F\x48\x39\x88", "eldenring.exe")
    return address + pm.read_int(address + 3) + 7


def get_eventflagman(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x3D....\x48\x85\xFF..\x32\xC0\xE9", "eldenring.exe")
    return address + pm.read_int(address + 3) + 7


def get_address_with_offsets(pm: Pymem, addr: int, offsets: list) -> int:
    try:
        for i in offsets:
            if i != offsets[-1]:
                addr = pm.read_longlong(addr + i)
        return addr + offsets[-1]
    except:
        print("couldn't read address")
        return -1


def get_addr_from_list(pm: Pymem, addr_list: list) -> int:
    try:
        x = 0
        if addr_list[0] == "worldchrman":
            x = pm.read_longlong(get_worldchrman(pm))
        elif addr_list[0] == "eventflagman":
            x = pm.read_longlong(get_eventflagman(pm))
        elif addr_list[0] == "gamedataman":
            x = pm.read_longlong(get_gamedataman(pm))
        elif addr_list[0] == "csflipper":
            x = pm.read_longlong(get_cs_flipper(pm))
        else:
            return -1
        return get_address_with_offsets(pm, x, addr_list[1])
    except:
        print("couldn't read address")
        return -1


def get_cs_lua_event(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x05....\x48\x85\xC0\x74.\x41\xBE\x01\x00\x00\x00\x44\x89\x75",
        "eldenring.exe",
    )
    return pm.read_longlong(address + pm.read_int(address + 3) + 7)


def get_lua_warp(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\xC3......\x57\x48\x83\xEC.\x48\x8B\xFA\x44", "eldenring.exe")
    return address + 2


def get_chr_count_and_set(pm: Pymem):
    worldchrman = pm.read_longlong(get_worldchrman(pm))
    chrset = pm.read_longlong(worldchrman + 0x1E1C8)
    chr_count = pm.read_int(chrset + 0x20)
    chrset = pm.read_longlong(chrset + 0x18)
    return chr_count, chrset


def get_dungeon_chr_count_and_set(pm: Pymem):
    worldchrman = pm.read_longlong(get_worldchrman(pm))
    chrset = pm.read_longlong(worldchrman + 0x1CC60)
    chr_count = pm.read_int(chrset + 0x10)
    chrset = pm.read_longlong(chrset + 0x18)
    return chr_count, chrset


def get_chr_dbg_flags(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x80\x3D....\x00\x0F\x85....\x32\xC0\x48", "eldenring.exe")
    return address + pm.read_int(address + 2) + 7


def get_spawn_addr(pm: Pymem, worldchrman) -> int:
    addr = worldchrman
    addr = pm.read_longlong(addr) + 0x1E1C0
    addr = pm.read_longlong(addr) + 0x18
    return pm.read_longlong(addr)


def get_gamedataman(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x05....\x48\x85\xC0\x74\x05\x48\x8B\x40\x58\xC3\xC3",
        "eldenring.exe",
    )
    return address + pm.read_int(address + 3) + 7


def get_cs_flipper(pm: Pymem) -> int:
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x0D....\x80\xBB\xD7\x00\x00\x00\x00\x0F\x84\xCE\x00\x00\x00\x48\x85\xC9\x75\x2E",
        "eldenring.exe",
    )
    return address + pm.read_int(address + 3) + 7

def get_flask(pm: Pymem):
    return get_address_with_offsets(pm, pm.read_longlong(pm.base_address+0x044FF328), [0xB0, 0x80, 0xF8, 0x134])

def get_field_area(pm: Pymem):
    address = pm.pattern_scan_module(
        rb"\x48\x8B\x0D....\x48...\x44\x0F\xB6\x61.\xE8....\x48\x63\x87....\x48...\x48\x85\xC0",
        "eldenring.exe",
    )
    return address + pm.read_int(address + 3) + 7





def p(v):  # For debug purposes, print address in nice format
    if isinstance(v, list):
        print([format(i) for i in v])
    elif isinstance(v, dict):
        for key, value in v.items():
            print(f"{key}  {format(value,'X')}")
    else:
        print(format(v, "X"))


def get_random_func():
    with open("resources/effects_list.json", "r") as json_file:
        data = json.load(json_file)

    active_functions = [item for item in data if item["active"] == 1]

    effect_module = import_module("effects.effects")
    effect_functions = [
        getattr(effect_module, item["name"]) for item in active_functions
    ]

    chances = [item["chance"] for item in active_functions]
    random_effect = choices(effect_functions, chances)[0]
    index = effect_functions.index(random_effect)

    return (
        random_effect,
        active_functions[index]["description"],
        active_functions[index]["sleep_time"],
    )


def get_dbg_func(i):
    with open('resources/effects_list.json', 'r') as json_file:
        data = json.load(json_file)
    active_functions = [item for item in data if item['active'] == 1]
    effect_module = import_module('effects.effects')
    effect_functions = [
        getattr(effect_module, item['name']) for item in active_functions
    ]
    return effect_functions[i], active_functions[i][
        'description'], active_functions[i]['sleep_time']
