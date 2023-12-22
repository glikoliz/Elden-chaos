import pymem
from time import sleep
from random import randint, choice, shuffle
from linecache import getline


class Funcs:
    def disable_fast_travel(pm, final_list):
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )

    def enable_fast_travel(pm, final_list):  # TODO:can be better
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x00\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )

    def warp_to(pm, final_list, grace):
        warp_func = pm.allocate(100)
        cs_lua_event = final_list["CS_LUA_EVENT"].to_bytes(8, byteorder="little")
        lua_warp = final_list["LUA_WARP"].to_bytes(8, byteorder="little")
        bytecode = (
            b"\x48\x83\xEC\x48"
            b"\x48\xB8" + cs_lua_event + b"\x48\x8B\x48\x18"
            b"\x48\x8B\x50\x08"
            b"\x8B\x05\x1C\x00\x00\x00"
            b"\x44\x8D\x80\x18\xFC\xFF\xFF\xFF\x15\x02\x00\x00\x00"
            b"\xEB\x08" + lua_warp + b"\x48\x83\xC4\x48"
            b"\xC3"
        )
        warp_loc = warp_func + len(bytecode)
        # addr=pm.allocate(len(bytecode))
        pm.write_bytes(warp_func, bytecode, len(bytecode))
        pm.write_int(warp_loc, grace)
        pm.start_thread(warp_func)

        pm.free(warp_func)

    def wait(pm, final_list, wait_time):
        sleep(wait_time)
        while pm.read_int(final_list["CUTSCENE_ON"]) != 0:
            sleep(0.1)
    
    def change_model_size(pm, addr, x, y, z):
        pm.write_float(addr, x)
        pm.write_float(addr+4, y)
        pm.write_float(addr+8, z)

    def respawn_boss(pm, boss_addr):
        pm.write_uchar(boss_addr, 0)

    def spawn_enemy(pm, final_list, id):  # TODO:chr_count may be broken
        pm.write_bytes(
            final_list["SPAWN_NPC_X"], pm.read_bytes(final_list["CURRENT_POS"], 12), 12
        )  # WRITE CURRENT POS

        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        pm.write_bytes(final_list["CHR_ID"], chr_id, len(chr_id))
        pm.write_int(final_list["NPC_PARAM_ID"], id * 10000)
        pm.write_int(final_list["NPC_THINK_PARAM_ID"], id * 10000)
        pm.write_int(final_list["EVENT_ENTITY_ID"], 0)
        pm.write_int(final_list["TALK_ID"], 0)
        pm.write_bytes(final_list["NPC_ENEMY_TYPE"], b"\x00", 1)
        # WRITE CHR INFO #
        spawned_enemy = final_list["SPAWN_ADDR"].to_bytes(8, byteorder="little")
        worldchrman = final_list["WORLDCHRMAN"].to_bytes(8, byteorder="little")
        assembly_code = (
            b"\x48\xA1" + worldchrman + 
            b"\x48\x8B\x80\x40\xE6\x01\x00"
            b"\xC6\x40\x44\x01"
            b"\x8B\x15\x30\x00\x00\x00"
            b"\x6B\xD2\x10"
            b"\x48\xBB" + spawned_enemy + 
            b"\x48\x01\xD3"
            b"\x8A\x80\x78\x01\x00\x00"
            b"\x88\x43\x0B"
            b"\xFF\x05\x11\x00\x00\x00"
            b"\xC3"
        )
        l = pm.allocate(100)
        # print(format(l,'X'))
        pm.write_bytes(l, assembly_code, len(assembly_code))
        pm.start_thread(l)
        # print(pm.read_int(l+0x4B))
        pm.free(l)


def get_random_function():
    functions = [
        (OHKO, "One Hit KO"),
        (MANA_LEAK, "Mana leak"),
        (WARP_TO_RANDOM_GRACE, "Teleport to random grace"),
        (GODRICK_TIME, "Git Gud"),
        (SPAWN_MALENIA, "Spawn Melania"),
        (DISABLE_GRAVITY, "Disable gravity"),
        (GO_REST, "Go rest"),
        (INVINCIBILITY, "Invincibility"),
        (INVISIBILITY, "Invisibility"),
        (GHOST, "Casper mode"),
        (POOR_TARNISHED, "Poor Tarnished"),
        (RICH_TARNISHED, "Rich Tarnished"),
        (CHANGE_GENDER, "Change Gender"),
        (RANDOM_STATS, "Random Stats"),
        (SONIC_SPEED, "Sonic Speed"),
        (SLOW_CHR, "Turtle speed"),
        (FULL_STAMINA, "Unlimited Stamina"),
        (LVL1_CROOK, "LVL1 Crook"),
        (LVL99_BOSS, "LVL99 Boss")
    ]
    random_function, function_name = choice(functions)
    return random_function, function_name


def dbg_get_func(i):
    functions = [
        (OHKO, "One Hit KO"),
        (MANA_LEAK, "Mana leak"),
        (WARP_TO_RANDOM_GRACE, "Teleport to random grace"),
        (GODRICK_TIME, "Git Gud"),
        (SPAWN_MALENIA, "Spawn Melania"),
        (DISABLE_GRAVITY, "Disable gravity"),
        (GO_REST, "Go rest"),
        (INVINCIBILITY, "Invincibility"),
        (INVISIBILITY, "Invisibility"),
        (GHOST, "Casper mode"),
        (POOR_TARNISHED, "Poor Tarnished"),
        (CHANGE_GENDER, "Change Gender"),
        (RANDOM_STATS, "Random Stats"),
        (SONIC_SPEED, "Sonic Speed"),
        (SLOW_CHR, "Slow-mo"),
        (LVL1_CROOK, "LVL1 Crook"),
        (FULL_STAMINA, "Unlimited Stamina"),
        (LVL99_BOSS, "LVL99 Boss"),
        # (DWARF_MODE, "5'11 Experience"),
        # (BIG_BOY, "Big Boy"),
        (RICH_TARNISHED, "Rich Tarnished"),
        (BUFF, "Buff"),
        (HUSSEIN, "Saddam Hussein"),
        (CYBERPUNK_EXPERIENCE, "Cyberpunk Experience")
    ]
    return functions[len(functions)-i-1]


def OHKO(pm, final_list):
    basehp = pm.read_int(final_list["MAX_HP"])
    pm.write_int(final_list["MAX_HP"], 1)
    Funcs.wait(pm, final_list, 10)
    pm.write_int(final_list["MAX_HP"], basehp)


def MANA_LEAK(pm, final_list):
    fp = pm.read_int(final_list["FP"])
    while fp >= 3 and pm.read_int(final_list["CUTSCENE_ON"]) == 0:
        fp = pm.read_int(final_list["FP"]) - 3
        pm.write_int(final_list["FP"], fp)
        sleep(0.5)


def WARP_TO_RANDOM_GRACE(pm, final_list):
    random_number = int(getline("graces.txt", randint(0, 305)).strip())
    Funcs.warp_to(pm, final_list, random_number)


def GODRICK_TIME(pm, final_list):
    Funcs.respawn_boss(pm, final_list["GODRICK"])
    Funcs.disable_fast_travel(pm, final_list)
    Funcs.warp_to(pm, final_list, 18002950)
    while pm.read_uchar(final_list["GODRICK"]) == 0 and pm.read_int(final_list["CUTSCENE_ON"]) == 0:  # wait until godrick(or character) dies
        sleep(1)
        pass
    Funcs.enable_fast_travel(pm, final_list)


def SPAWN_MALENIA(pm, final_list):
    Funcs.spawn_enemy(pm, final_list, 2120)


def DISABLE_GRAVITY(pm, final_list):
    pm.write_bytes(final_list["DISABLE_GRAVITY"], b"\x01", 1)
    sleep(10)
    pm.write_bytes(final_list["DISABLE_GRAVITY"], b"\x00", 1)


def GO_REST(pm, final_list):
    pm.write_float(final_list["ANIMATION_SPEED"], 0.0)
    sleep(10)
    pm.write_float(final_list["ANIMATION_SPEED"], 1.0)


def INVINCIBILITY(pm, final_list):
    pm.write_bytes(final_list["NO_DEAD"], b"\x01", 1)
    sleep(10)
    pm.write_bytes(final_list["NO_DEAD"], b"\x00", 1)


def INVISIBILITY(pm, final_list):
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 8, b"\x01", 1)  # hide player
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 9, b"\x01", 1)  # silence player
    # pm.write_int(final_list['CHR_MODEL'], 3)
    sleep(20)
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 8, b"\x00", 1)
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 9, b"\x00", 1)
    # pm.write_int(final_list['CHR_MODEL'], 0)


def GHOST(pm, final_list):
    pm.write_int(final_list["CHR_MODEL"], 3)
    sleep(20)
    pm.write_int(final_list["CHR_MODEL"], 0)


def POOR_TARNISHED(pm, final_list):
    pm.write_int(final_list["RUNES"], 0)


def RICH_TARNISHED(pm, final_list):
    pm.write_int(final_list["RUNES"], pm.read_int(final_list["TOTAL_RUNES"]) // 10)


def CHANGE_GENDER(pm, final_list):
    if pm.read_bytes(final_list["GENDER"], 1) == b"\x01":
        pm.write_bytes(final_list["GENDER"], b"\x00", 1)
    else:
        pm.write_bytes(final_list["GENDER"], b"\x01", 1)


def RANDOM_STATS(pm, final_list):
    target_sum = pm.read_int(final_list["CURRENT_LEVEL"])
    addr = final_list["STATS"]
    if target_sum > 7:
        numbers = [randint(1, target_sum - 7) for _ in range(7)]
        numbers.append(target_sum - sum(numbers))
        while any(num < 1 for num in numbers):
            numbers = [randint(1, target_sum - 7) for _ in range(7)]
            numbers.append(target_sum - sum(numbers))
        shuffle(numbers)
        for i in range(8):
            pm.write_int(addr + 4 * i, numbers[i])
    # pass


def SONIC_SPEED(pm, final_list):
    pm.write_float(final_list["ANIMATION_SPEED"], 3.0)
    sleep(10)
    pm.write_float(final_list["ANIMATION_SPEED"], 1.0)


def SLOW_CHR(pm, final_list):
    pm.write_float(final_list["ANIMATION_SPEED"], 0.3)
    sleep(10)
    pm.write_float(final_list["ANIMATION_SPEED"], 1.0)


def FULL_STAMINA(pm, final_list):
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 4, b"\x01", 1)
    sleep(10)
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 4, b"\x00", 1)
    
    
def LVL1_CROOK(pm, final_list):
    addr = final_list["STATS"]
    current_stats = pm.read_bytes(addr, 32)
    hp, fp=pm.read_int(final_list['HP']), pm.read_int(final_list['FP'])
    for i in range(8):
        pm.write_int(addr + 4 * i, 1)
    Funcs.wait(pm, final_list, 10)
    pm.write_bytes(final_list['STATS'], current_stats, len(current_stats))
    pm.write_int(final_list['HP'], hp)
    pm.write_int(final_list['FP'], fp)
    
def LVL99_BOSS(pm, final_list):
    addr = final_list["STATS"]
    current_stats = pm.read_bytes(addr, 32)
    for i in range(8):
        pm.write_int(addr + 4 * i, 99)
    Funcs.wait(pm, final_list, 10)
    pm.write_bytes(final_list['STATS'], current_stats, len(current_stats))


def DWARF_MODE(pm, final_list):
    addr = final_list["CHR_SIZE"]
    Funcs.change_model_size(pm, addr, 0.3, 0.3, 0.3)
    sleep(10)
    Funcs.change_model_size(pm, addr,1.0, 1.0, 1.0)
    

def BIG_BOY(pm, final_list):
    addr = final_list["CHR_SIZE"]
    Funcs.change_model_size(pm, addr, 2.0, 2.0, 2.0)
    sleep(10)
    Funcs.change_model_size(pm, addr,1.0, 1.0, 1.0)
    
def HUSSEIN(pm, final_list): 
    pm.write_int(final_list["ANIMATION"], 67011)
    pm.write_float(final_list["ANIMATION_SPEED"], 15.0)
    pm.write_int(final_list["CHR_MODEL"], 2)
    sleep(0.3)
    pm.write_float(final_list["ANIMATION_SPEED"], 1.0)
    sleep(10)
    pm.write_int(final_list["ANIMATION"], 0)
    pm.write_int(final_list["CHR_MODEL"], 0)

def BUFF(pm, final_list): #TODO: make more buffs
    addr = final_list["CHR_SIZE"]
    pm.write_int(final_list["ANIMATION"], 60470)
    sleep(6)
    Funcs.change_model_size(pm, addr, 1.7, 1.7, 1.7)
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 2, b"\x01", 1)
    pm.write_int(final_list["ANIMATION"], 60471)
    sleep(10)
    Funcs.change_model_size(pm, addr, 1.0, 1.0, 1.0)
    pm.write_bytes(final_list["CHR_DBG_FLAGS"] + 2, b"\x00", 1)
    
def CYBERPUNK_EXPERIENCE(pm, final_list): 
    pm.write_float(final_list['FPS'], 20.0)
    pm.write_bytes(final_list['USE_FPS'], b'\x01', 1)
    pm.write_int(final_list['ANIMATION'], 60265)
    sleep(1)
    pm.write_int(final_list['ANIMATION'], 0)
    sleep(10)
    pm.write_bytes(final_list['USE_FPS'], b'\x00', 1)
    