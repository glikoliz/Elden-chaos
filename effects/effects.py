import pymem
from time import sleep
from random import randint, shuffle, uniform
from linecache import getline
from lib.funcs import Funcs
from lib.getaddress import get_addr_from_list, get_chr_dbg_flags, get_worldchrman, get_address_with_offsets, get_chr_count_and_set
import json


def OHKO():
    Funcs.wait(0)  # if player in a cutscene wait until it ends
    basehp_addr = get_addr_from_list(pm, addr_list["MAX_HP"])
    basehp = pm.read_int(basehp_addr)
    pm.write_int(basehp_addr, 1)
    Funcs.wait(10)
    try:
        if pm.read_int(basehp_addr) == 1:
            pm.write_int(basehp_addr, basehp)
    except:
        pass


def MANA_LEAK():
    Funcs.wait(0)
    cutscene_on = get_addr_from_list(pm, addr_list["CUTSCENE_ON"])
    fp_addr = get_addr_from_list(pm, addr_list["FP"])
    fp = pm.read_int(fp_addr)
    while fp >= 3 and pm.read_int(cutscene_on) == 0:
        fp = pm.read_int(fp_addr) - 3
        pm.write_int(fp_addr, fp)
        sleep(0.5)


def WARP_TO_RANDOM_GRACE():
    random_number = int(getline("resources/graces.txt", randint(0, 305)).strip())
    Funcs.warp_to(random_number)


def GODRICK_TIME():
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


def SPAWN_MALENIA():
    Funcs.spawn_enemy(2120)


def DISABLE_GRAVITY():
    Funcs.wait(0)
    pm.write_bytes(get_addr_from_list(pm, addr_list["DISABLE_GRAVITY"]), b"\x01", 1)
    Funcs.wait(20)
    pm.write_bytes(get_addr_from_list(pm, addr_list["DISABLE_GRAVITY"]), b"\x00", 1)


def GO_REST():  # TODO:Make player invincible while he is afk
    Funcs.wait(0)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 0.0)
    Funcs.wait(10)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def INVINCIBILITY():
    Funcs.wait(0)
    pm.write_bytes(get_addr_from_list(pm, addr_list["NO_DEAD"]), b"\x01", 1)
    Funcs.wait(10)
    pm.write_bytes(get_addr_from_list(pm, addr_list["NO_DEAD"]), b"\x00", 1)


def INVISIBILITY():
    Funcs.wait(0)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 8, b"\x01", 1)  # hide player
    pm.write_bytes(chr_dbg_flags + 9, b"\x01", 1)  # silence player
    Funcs.wait(20)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 8, b"\x00", 1)
    pm.write_bytes(chr_dbg_flags + 9, b"\x00", 1)


def GHOST():
    Funcs.wait(0)
    pm.write_int(get_addr_from_list(pm, addr_list["CHR_MODEL"]), 3)
    Funcs.wait(10)
    pm.write_int(get_addr_from_list(pm, addr_list["CHR_MODEL"]), 0)


def POOR_TARNISHED():
    pm.write_int(get_addr_from_list(pm, addr_list["RUNES"]), 0)


def RICH_TARNISHED():
    runes_addr = get_addr_from_list(pm, addr_list["RUNES"])
    pm.write_int(
        runes_addr,
        pm.read_int(runes_addr)
        + (pm.read_int(get_addr_from_list(pm, addr_list["TOTAL_RUNES"])) // 10),
    )


def CHANGE_GENDER():
    gender_addr = get_addr_from_list(pm, addr_list["GENDER"])
    if pm.read_bytes(gender_addr, 1) == b"\x01":
        pm.write_bytes(gender_addr, b"\x00", 1)
    else:
        pm.write_bytes(gender_addr, b"\x01", 1)


def RANDOM_STATS():
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


def SONIC_SPEED():
    Funcs.wait(0)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 3.0)
    Funcs.wait(10)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def SLOW_CHR():
    Funcs.wait(0)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 0.3)
    Funcs.wait(10)
    pm.write_float(get_addr_from_list(pm, addr_list["ANIMATION_SPEED"]), 1.0)


def FULL_STAMINA():
    Funcs.wait(0)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 4, b"\x01", 1)
    Funcs.wait(10)
    chr_dbg_flags = get_chr_dbg_flags(pm)
    pm.write_bytes(chr_dbg_flags + 4, b"\x00", 1)


def LVL1_CROOK():
    Funcs.wait(0)
    addr = get_addr_from_list(pm, addr_list["STATS"])
    current_stats = pm.read_bytes(addr, 32)
    hp, fp = pm.read_int(get_addr_from_list(pm, addr_list["HP"])), pm.read_int(
        get_addr_from_list(pm, addr_list["FP"])
    )
    for i in range(8):
        pm.write_int(addr + 4 * i, 1)
    # Funcs.wait(pm, address_list, 10)
    Funcs.wait(10)
    pm.write_bytes(
        get_addr_from_list(pm, addr_list["STATS"]), current_stats, len(current_stats)
    )
    pm.write_int(get_addr_from_list(pm, addr_list["HP"]), hp)
    pm.write_int(get_addr_from_list(pm, addr_list["FP"]), fp)


def LVL99_BOSS():
    addr = get_addr_from_list(pm, addr_list["STATS"])
    current_stats = pm.read_bytes(addr, 32)
    for i in range(8):
        pm.write_int(addr + 4 * i, 99)
    Funcs.wait(10)
    pm.write_bytes(
        get_addr_from_list(pm, addr_list["STATS"]), current_stats, len(current_stats)
    )


def DWARF_MODE():  # TODO: hide cloth for every model size change
    Funcs.wait(0)
    Funcs.hide_cloth()
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 0.3, 0.3, 0.3
    )
    Funcs.wait(10)
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0
    )
    Funcs.show_cloth()
    


def BIG_BOY():
    Funcs.wait(0)
    Funcs.hide_cloth()
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 2.0, 2.0, 2.0
    )
    Funcs.wait(10)
    Funcs.change_model_size(
        get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0
    )
    Funcs.show_cloth()
    


def RANDOM_MODEL_SIZE():
    Funcs.wait(0)
    Funcs.hide_cloth()
    Funcs.change_model_size(get_addr_from_list(pm, addr_list["CHR_SIZE"]), uniform(0.1, 2.5), uniform(0.1, 2.5), uniform(0.1, 2.5))
    Funcs.wait(10)
    Funcs.change_model_size(get_addr_from_list(pm, addr_list["CHR_SIZE"]), 1.0, 1.0, 1.0)
    Funcs.show_cloth()
    


def HUSSEIN():
    animation = get_addr_from_list(pm, addr_list["ANIMATION"])
    animation_speed = get_addr_from_list(pm, addr_list["ANIMATION_SPEED"])
    chr_model = get_addr_from_list(pm, addr_list["CHR_MODEL"])

    pm.write_int(animation, 67011)
    pm.write_float(animation_speed, 15.0)
    pm.write_int(chr_model, 2)
    sleep(0.3)
    pm.write_float(animation_speed, 1.0)
    Funcs.wait(10)
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


def CYBERPUNK_EXPERIENCE():
    Funcs.wait(0)
    collision_addr=pm.pattern_scan_module(b'\xC6\x83\x78\x0D\x00\x00\xFF', 'eldenring.exe')
    pm.write_bytes(collision_addr, b'\xC6\x83\x78\x0D\x00\x00\x02', 7)
    pm.write_float(get_addr_from_list(pm, addr_list["FPS"]), 20.0)
    pm.write_bytes(get_addr_from_list(pm, addr_list["USE_FPS"]), b"\x01", 1)
    pm.write_int(get_addr_from_list(pm, addr_list["ANIMATION"]), 60265)
    sleep(1.5)
    pm.write_int(get_addr_from_list(pm, addr_list["ANIMATION"]), 0)
    Funcs.wait(10)
    pm.write_bytes(get_addr_from_list(pm, addr_list["USE_FPS"]), b"\x00", 1)
    pm.write_bytes(collision_addr, b'\xC6\x83\x78\x0D\x00\x00\xFF', 7)

def SPEED_EVERYONE():
    chr_count, chrset=get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemyins=pm.read_longlong(chrset+i*0x10)
        if(enemyins):
            speed=get_address_with_offsets(pm, enemyins, [0x190, 0x28, 0x17C8])
            pm.write_float(speed, 2.0)
    Funcs.wait(10)
    chr_count, chrset=get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemyins=pm.read_longlong(chrset+i*0x10)
        if(enemyins):
            speed=get_address_with_offsets(pm, enemyins, [0x190, 0x28, 0x17C8])
            pm.write_float(speed, 1.0)
        
def SLOW_EVERYONE():
    chr_count, chrset=get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemyins=pm.read_longlong(chrset+i*0x10)
        if(enemyins):
            speed=get_address_with_offsets(pm, enemyins, [0x190, 0x28, 0x17C8])
            pm.write_float(speed, 0.3)
    Funcs.wait(10)
    chr_count, chrset=get_chr_count_and_set(pm)
    for i in range(1, chr_count):
        enemyins=pm.read_longlong(chrset+i*0x10)
        if(enemyins):
            speed=get_address_with_offsets(pm, enemyins, [0x190, 0x28, 0x17C8])
            pm.write_float(speed, 1.0)

def TP_EVERYONE_TO_PLAYER():
    player_coords=get_addr_from_list(pm, addr_list['CURRENT_POS'])
    chr_count, chrset=get_chr_count_and_set(pm)
    player_x,player_y,player_z=pm.read_float(player_coords), pm.read_float(player_coords+0x04), pm.read_float(player_coords+0x08)
    for i in range(1, chr_count):
        enemyins=pm.read_longlong(chrset+i*0x10)
        if(enemyins):
            alliance=get_address_with_offsets(pm, enemyins, [0x6C])
            if(pm.read_bytes(alliance, 1)==b'\x06'):
                coords=get_address_with_offsets(pm, enemyins, [0x190, 0x68, 0x0])+0x70
                pm.write_float(coords, player_x)
                pm.write_float(coords+0x04, player_y)
                pm.write_float(coords+0x08, player_z)

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
