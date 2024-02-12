import pymem
from time import sleep
from random import randint, shuffle, uniform
from linecache import getline
from lib.funcs import Funcs
from lib.getaddress import (
    get_addr_from_list,
    get_chr_dbg_flags,
    get_worldchrman,
    get_address_with_offsets,
    get_chr_count_and_set,
    get_dungeon_chr_count_and_set,
    get_flask
)
import json


def OHKO(sleep_time: int):
    basehp_addr = get_addr_from_list(pm, addr_list["MAX_HP"])
    basehp = pm.read_int(basehp_addr)
    pm.write_int(basehp_addr, 1)
    Funcs.wait(sleep_time)
    try:
        if pm.read_int(basehp_addr) == 1:
            pm.write_int(basehp_addr, basehp)
    except:
        pass


def MANA_LEAK(sleep_time: int):
    cutscene_on = get_addr_from_list(pm, addr_list["CUTSCENE_ON"])
    fp_addr = get_addr_from_list(pm, addr_list["FP"])
    fp = pm.read_int(fp_addr)
    while fp >= 3 and pm.read_int(cutscene_on) == 0:
        fp = pm.read_int(fp_addr) - 3
        pm.write_int(fp_addr, fp)
        sleep(0.5)


def WARP_TO_RANDOM_GRACE(sleep_time: int):
    random_number = int(getline("resources/graces.txt", randint(0, 305)).strip())
    Funcs.wait(0)
    Funcs.warp_to(random_number)


def GODRICK_TIME(sleep_time: int):
    godrick_addr = get_addr_from_list(pm, addr_list["GODRICK"])
    cutscene_on = get_addr_from_list(pm, addr_list["CUTSCENE_ON"])
    Funcs.respawn_boss(godrick_addr)
    Funcs.disable_fast_travel()
    Funcs.warp_to(18002950)
    Funcs.wait(3)
    while (
        pm.read_uchar(godrick_addr) == 0 and pm.read_int(cutscene_on) == 0
    ):  # wait until godrick(or character) dies
        sleep(1)
        pass
    Funcs.enable_fast_travel()


def SPAWN_MALENIA(sleep_time: int):
    Funcs.spawn_enemy(2120)


def DISABLE_GRAVITY(sleep_time: int):
    pm.write_bytes(get_addr_from_list(pm, addr_list["DISABLE_GRAVITY"]), b"\x01", 1)
    Funcs.wait(sleep_time)
    pm.write_bytes(get_addr_from_list(pm, addr_list["DISABLE_GRAVITY"]), b"\x00", 1)


def GO_REST(sleep_time: int):  # TODO:Make player invincible while he is afk
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 0.0)
    Funcs.wait(sleep_time)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def INVINCIBILITY(sleep_time: int):
    pm.write_bytes(get_addr_from_list(pm, addr_list["NO_DEAD"]), b"\x01", 1)
    Funcs.wait(sleep_time)
    pm.write_bytes(get_addr_from_list(pm, addr_list["NO_DEAD"]), b"\x00", 1)


def INVISIBILITY(sleep_time: int):
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 8, b"\x01", 1)  # hide player
    pm.write_bytes(chr_dbg_flags + 9, b"\x01", 1)  # silence player
    Funcs.wait(sleep_time)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 8, b"\x00", 1)
    pm.write_bytes(chr_dbg_flags + 9, b"\x00", 1)


def GHOST(sleep_time: int):
    pm.write_int(get_addr_from_list(pm, addr_list["CHR_MODEL"]), 3)
    Funcs.wait(sleep_time)
    pm.write_int(get_addr_from_list(pm, addr_list["CHR_MODEL"]), 0)


def POOR_TARNISHED(sleep_time: int):
    pm.write_int(get_addr_from_list(pm, addr_list["RUNES"]), 0)


def RICH_TARNISHED(sleep_time: int):
    runes_addr = get_addr_from_list(pm, addr_list["RUNES"])
    pm.write_int(
        runes_addr,
        pm.read_int(runes_addr)
        + (pm.read_int(get_addr_from_list(pm, addr_list["TOTAL_RUNES"])) // 10),
    )


def CHANGE_GENDER(sleep_time: int):
    gender_addr = get_addr_from_list(pm, addr_list["GENDER"])
    if pm.read_bytes(gender_addr, 1) == b"\x01":
        pm.write_bytes(gender_addr, b"\x00", 1)
    else:
        pm.write_bytes(gender_addr, b"\x01", 1)


def RANDOM_STATS(sleep_time: int):
    target_sum = pm.read_int(get_addr_from_list(pm, addr_list["CURRENT_LEVEL"]))
    addr = get_addr_from_list(pm, addr_list["STATS"])
    if target_sum > 7:
        numbers = [randint(1, target_sum - 7) for _ in range(7)]
        numbers.append(target_sum - sum(numbers))
        while any(num < 1 for num in numbers):
            numbers = [randint(1, target_sum - 7) for _ in range(7)]
            numbers.append(target_sum - sum(numbers))
        shuffle(numbers)
        for i in range(8):
            pm.write_int(addr + 4 * i, numbers[i])


def SONIC_SPEED(sleep_time: int):
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 3.0)
    Funcs.wait(sleep_time)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def SLOW_CHR(sleep_time: int):
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 0.3)
    Funcs.wait(sleep_time)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def FULL_STAMINA(sleep_time: int):
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 4, b"\x01", 1)
    Funcs.wait(sleep_time)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 4, b"\x00", 1)


def LVL1_CROOK(sleep_time: int):
    addr = get_addr_from_list(pm, addr_list["STATS"])
    current_stats = pm.read_bytes(addr, 32)
    hp, fp = pm.read_int(get_addr_from_list(pm, addr_list["HP"])), pm.read_int(
        get_addr_from_list(pm, addr_list["FP"])
    )
    for i in range(8):
        pm.write_int(addr + 4 * i, 1)
    # Funcs.wait(pm, address_list, 10)
    Funcs.wait(sleep_time)
    pm.write_bytes(
        get_addr_from_list(pm, addr_list["STATS"]), current_stats, len(current_stats)
    )
    pm.write_int(get_addr_from_list(pm, addr_list["HP"]), hp)
    pm.write_int(get_addr_from_list(pm, addr_list["FP"]), fp)


def LVL99_BOSS(sleep_time: int):
    addr = get_addr_from_list(pm, addr_list["STATS"])
    current_stats = pm.read_bytes(addr, 32)
    for i in range(8):
        pm.write_int(addr + 4 * i, 99)
    Funcs.wait(sleep_time)
    pm.write_bytes(
        get_addr_from_list(pm, addr_list["STATS"]), current_stats, len(current_stats)
    )


def DWARF_MODE(sleep_time: int):
    Funcs.hide_cloth()
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 0.3, 0.3, 0.3
    )
    Funcs.wait(sleep_time)
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0
    )
    Funcs.show_cloth()


def BIG_BOY(sleep_time: int):
    Funcs.hide_cloth()
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 2.0, 2.0, 2.0
    )
    Funcs.wait(sleep_time)
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0
    )
    Funcs.show_cloth()


def RANDOM_MODEL_SIZE(sleep_time: int):
    Funcs.hide_cloth()
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]),
        uniform(0.1, 2.5),
        uniform(0.1, 2.5),
        uniform(0.1, 2.5),
    )
    Funcs.wait(sleep_time)
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0
    )
    Funcs.show_cloth()


def HUSSEIN(sleep_time: int):
    animation = get_addr_from_list(pm, addr_list["ANIMATION"])
    animation_speed = get_addr_from_list(pm, addr_list["ANIMATION_SPEED"])
    chr_model = get_addr_from_list(pm, addr_list["CHR_MODEL"])

    pm.write_int(animation, 67011)
    pm.write_float(animation_speed, 15.0)
    pm.write_int(chr_model, 2)
    sleep(0.3)
    pm.write_float(animation_speed, 1.0)
    Funcs.wait(sleep_time)
    pm.write_int(animation, 0)
    pm.write_int(chr_model, 0)


# def BUFF(address_list):  # TODO: make more buffs
#     """
#     Player go throught portal and get some buffs
#     """
#     addr = address_list["CHR_SIZE"]
#     pm.write_int(address_list["ANIMATION"], 60470)
#     sleep(6)
#     Funcs.change_model_size(pm, addr, 1.7, 1.7, 1.7)
#     pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x01", 1)
#     pm.write_int(address_list["ANIMATION"], 60471)
#     sleep(10)
#     Funcs.change_model_size(pm, addr, 1.0, 1.0, 1.0)
#     pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x00", 1)


def CYBERPUNK_EXPERIENCE(sleep_time: int):
    collision_addr = pm.pattern_scan_module(
        b"\xC6\x83\x78\x0D\x00\x00\xFF", "eldenring.exe"
    )
    pm.write_bytes(collision_addr, b"\xC6\x83\x78\x0D\x00\x00\x02", 7)
    pm.write_float(get_addr_from_list(pm, addr_list["FPS"]), 20.0)
    pm.write_bytes(get_addr_from_list(pm, addr_list["USE_FPS"]), b"\x01", 1)
    pm.write_int(get_addr_from_list(pm, addr_list["ANIMATION"]), 60265)
    sleep(1.5)
    pm.write_int(get_addr_from_list(pm, addr_list["ANIMATION"]), 0)
    Funcs.wait(sleep_time)
    pm.write_bytes(get_addr_from_list(pm, addr_list["USE_FPS"]), b"\x00", 1)
    pm.write_bytes(collision_addr, b"\xC6\x83\x78\x0D\x00\x00\xFF", 7)


def SPEED_EVERYONE(sleep_time: int):
    chr_count, chrset = get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemy_addr = pm.read_longlong(chrset + i * 0x10)
        if enemy_addr:
            try:
                speed = get_address_with_offsets(pm, enemy_addr, [0x190, 0x28, 0x17C8])
                pm.write_float(speed, 2.0)
            except:
                pass
    Funcs.wait(sleep_time)
    chr_count, chrset = get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemy_addr = pm.read_longlong(chrset + i * 0x10)
        if enemy_addr:
            try:
                speed = get_address_with_offsets(pm, enemy_addr, [0x190, 0x28, 0x17C8])
                pm.write_float(speed, 1.0)
            except:
                pass


def SLOW_EVERYONE(sleep_time: int):
    chr_count, chrset = get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemy_addr = pm.read_longlong(chrset + i * 0x10)
        if enemy_addr:
            try:
                speed = get_address_with_offsets(pm, enemy_addr, [0x190, 0x28, 0x17C8])
                pm.write_float(speed, 0.3)
            except:
                pass
    Funcs.wait(sleep_time)
    chr_count, chrset = get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemy_addr = pm.read_longlong(chrset + i * 0x10)
        if enemy_addr:
            try:
                speed = get_address_with_offsets(pm, enemy_addr, [0x190, 0x28, 0x17C8])
                pm.write_float(speed, 1.0)
            except:
                pass


def TP_EVERYONE_TO_PLAYER(sleep_time: int):
    current_pos_addr=get_addr_from_list(pm, addr_list["CURRENT_POS"])
    chr_count, chrset = get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemy_addr = pm.read_longlong(chrset + i * 0x10)
        if enemy_addr:
            try:
                if pm.read_bytes(enemy_addr+0x6C, 1) == b"\x06":
                    coords = (
                        get_address_with_offsets(pm, enemy_addr, [0x190, 0x68, 0x0])
                        + 0x70
                    )
                    pm.write_bytes(coords, pm.read_bytes(current_pos_addr, 12), 12)
            except Exception as e:
                print(e)
                pass

def TP_PLAYER_TO_NEARBY_ENEMY(sleep_time: int):
    player_coords=get_addr_from_list(pm, ["worldchrman", [124168, 400, 104, 112]])
    min_distance=Funcs.get_closest_enemy(player_coords)
    print(hex(min_distance[0]), min_distance[1])
    pm.write_bytes(player_coords, pm.read_bytes(min_distance[0], 12), 12)

def ONE_FLASK():
    crimson_flask=get_flask(pm)
    pm.write_bytes(crimson_flask, b'\x01', 1)
    pass

if __name__ != "__main__":
    pm = pymem.Pymem("eldenring.exe")
    with open("resources/addresses.json", "r") as file:
        json_data = json.load(file)
    addr_list = {}
    for obj in json_data:
        name = obj["name"]
        addr_list[name] = [
            obj["addr"],
            [int(element, 16) for element in obj["offsets"].split()],
        ]
        
