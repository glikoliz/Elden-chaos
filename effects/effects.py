from time import sleep, time
from random import randint, choice, shuffle
from linecache import getline
import re
from lib.funcs import Funcs
import pymem


def OHKO(address_list):
    """
    Set player's maximum HP to 1
    """
    basehp = pm.read_int(address_list["MAX_HP"])
    pm.write_int(address_list["MAX_HP"], 1)
    Funcs.wait(pm, address_list, 10)
    pm.write_int(address_list["MAX_HP"], basehp)


def MANA_LEAK(address_list):
    """
    Decreases FP(mana) by 3 every 0.5 seconds, as long as the player has enough FP and not in a cutscene
    """
    fp = pm.read_int(address_list["FP"])
    while fp >= 3 and pm.read_int(address_list["CUTSCENE_ON"]) == 0:
        fp = pm.read_int(address_list["FP"]) - 3
        pm.write_int(address_list["FP"], fp)
        sleep(0.5)


def WARP_TO_RANDOM_GRACE(address_list):
    """
    Teleport player to a random grace(who would've thought)
    """
    random_number = int(getline("lib/graces.txt", randint(0, 305)).strip())
    Funcs.warp_to(pm, address_list, random_number)


def GODRICK_TIME(address_list):
    """
    Respawns godrick, disable fast travel(you can't escape the god's wrath) and warp you to the Cave of Knowledge grace
    """
    Funcs.respawn_boss(pm, address_list["GODRICK"])
    Funcs.disable_fast_travel(pm)
    Funcs.warp_to(pm, address_list, 18002950)
    Funcs.wait(pm, address_list, 3)
    while (
        pm.read_uchar(address_list["GODRICK"]) == 0
        and pm.read_int(address_list["CUTSCENE_ON"]) == 0
    ):  # wait until godrick(or character) dies
        sleep(1)
        pass
    Funcs.enable_fast_travel(pm)


def SPAWN_MALENIA(address_list):
    """
    Spawn Malenia(no way)
    """
    Funcs.spawn_enemy(pm, address_list, 2120)


def DISABLE_GRAVITY(address_list):
    """
    Disables gravity(you can't go under your current z pos). If player jumps he probably would die
    """
    pm.write_bytes(address_list["DISABLE_GRAVITY"], b"\x01", 1)
    sleep(10)
    pm.write_bytes(address_list["DISABLE_GRAVITY"], b"\x00", 1)


def GO_REST(address_list): #TODO:Make player invincible while he is afk
    """
    Player can't move(only rotate)
    """
    pm.write_float(address_list["ANIMATION_SPEED"], 0.0)
    sleep(10)
    pm.write_float(address_list["ANIMATION_SPEED"], 1.0)


def INVINCIBILITY(address_list):
    """
    Player can't die. Even if he fell from a great height
    """
    pm.write_bytes(address_list["NO_DEAD"], b"\x01", 1)
    sleep(10)
    pm.write_bytes(address_list["NO_DEAD"], b"\x00", 1)


def INVISIBILITY(address_list):
    """
    Enemies can't see or hear player(unless he attack them(maybe))
    """
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 8, b"\x01", 1)  # hide player
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 9, b"\x01", 1)  # silence player
    # pm.write_int(address_list['CHR_MODEL'], 3)
    sleep(20)
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 8, b"\x00", 1)
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 9, b"\x00", 1)
    # pm.write_int(address_list['CHR_MODEL'], 0)


def GHOST(address_list):
    """
    Player turns into a ghost(like the other players running around), can't attack or be attacked
    """
    pm.write_int(address_list["CHR_MODEL"], 3)
    sleep(20)
    pm.write_int(address_list["CHR_MODEL"], 0)


def POOR_TARNISHED(address_list):
    """
    Remove all current runes
    """
    pm.write_int(address_list["RUNES"], 0)


def RICH_TARNISHED(address_list):
    """
    Give player 10% of his total earned runes
    """
    pm.write_int(
        address_list["RUNES"],
        pm.read_int(address_list["RUNES"])
        + (pm.read_int(address_list["TOTAL_RUNES"]) // 10),
    )


def CHANGE_GENDER(address_list):
    """
    Change gender of a player
    """
    if pm.read_bytes(address_list["GENDER"], 1) == b"\x01":
        pm.write_bytes(address_list["GENDER"], b"\x00", 1)
    else:
        pm.write_bytes(address_list["GENDER"], b"\x01", 1)


def RANDOM_STATS(address_list):
    """
    Redistributes stats of a player randomly
    """
    target_sum = pm.read_int(address_list["CURRENT_LEVEL"])
    addr = address_list["STATS"]
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


def SONIC_SPEED(address_list):
    """
    Sets the player's animation speed to 3
    """
    pm.write_float(address_list["ANIMATION_SPEED"], 3.0)
    sleep(10)
    pm.write_float(address_list["ANIMATION_SPEED"], 1.0)


def SLOW_CHR(address_list):
    """
    Sets the player's animation speed to 0.3
    """
    pm.write_float(address_list["ANIMATION_SPEED"], 0.3)
    sleep(10)
    pm.write_float(address_list["ANIMATION_SPEED"], 1.0)


def FULL_STAMINA(address_list):
    """
    Give player infinite stamina
    """
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 4, b"\x01", 1)
    sleep(10)
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 4, b"\x00", 1)


def LVL1_CROOK(address_list):
    """
    Change level of every stat to 1 for a short period of time
    """
    addr = address_list["STATS"]
    current_stats = pm.read_bytes(addr, 32)
    hp, fp = pm.read_int(address_list["HP"]), pm.read_int(address_list["FP"])
    for i in range(8):
        pm.write_int(addr + 4 * i, 1)
    Funcs.wait(pm, address_list, 10)
    pm.write_bytes(address_list["STATS"], current_stats, len(current_stats))
    pm.write_int(address_list["HP"], hp)
    pm.write_int(address_list["FP"], fp)


def LVL99_BOSS(address_list):
    """
    Change level of every stat to 99 for a short period of time
    """
    addr = address_list["STATS"]
    current_stats = pm.read_bytes(addr, 32)
    for i in range(8):
        pm.write_int(addr + 4 * i, 99)
    Funcs.wait(pm, address_list, 10)
    pm.write_bytes(address_list["STATS"], current_stats, len(current_stats))


def DWARF_MODE(address_list):
    """
    Change character model size to 1/3 of original
    """
    Funcs.change_model_size(pm, address_list["CHR_SIZE"], 0.3, 0.3, 0.3)
    sleep(10)
    Funcs.change_model_size(pm, address_list["CHR_SIZE"], 1.0, 1.0, 1.0)


def BIG_BOY(address_list):
    """
    Doubles character model size
    """
    Funcs.change_model_size(pm, address_list["CHR_SIZE"], 2.0, 2.0, 2.0)
    sleep(10)
    Funcs.change_model_size(pm, address_list["CHR_SIZE"], 1.0, 1.0, 1.0)


def HUSSEIN(address_list):
    """
    Set current animation to laying position and turn player red
    """
    pm.write_int(address_list["ANIMATION"], 67011)
    pm.write_float(address_list["ANIMATION_SPEED"], 15.0)
    pm.write_int(address_list["CHR_MODEL"], 2)
    sleep(0.3)
    pm.write_float(address_list["ANIMATION_SPEED"], 1.0)
    sleep(10)
    pm.write_int(address_list["ANIMATION"], 0)
    pm.write_int(address_list["CHR_MODEL"], 0)


def BUFF(address_list):  # TODO: make more buffs
    """
    Player go throught portal and get some buffs
    """
    addr = address_list["CHR_SIZE"]
    pm.write_int(address_list["ANIMATION"], 60470)
    sleep(6)
    Funcs.change_model_size(pm, addr, 1.7, 1.7, 1.7)
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x01", 1)
    pm.write_int(address_list["ANIMATION"], 60471)
    sleep(10)
    Funcs.change_model_size(pm, addr, 1.0, 1.0, 1.0)
    pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x00", 1)


def CYBERPUNK_EXPERIENCE(address_list):
    """
    Lock fps at 20, use t-pose for a sec and make some noise
    """
    pm.write_float(address_list["FPS"], 20.0)
    pm.write_bytes(address_list["USE_FPS"], b"\x01", 1)
    pm.write_int(address_list["ANIMATION"], 60265)
    sleep(1)
    pm.write_int(address_list["ANIMATION"], 0)
    sleep(10)
    pm.write_bytes(address_list["USE_FPS"], b"\x00", 1)


def wtf(address_list):
    fir = address_list["CHR_DBG"]
    pattern = re.compile(rb"\x90\x3D\xFC\x6F\xF6\x7F\x00\x00")
    start_time = time()

    module_data = pm.read_bytes(fir, 0x2806F000)
    matches = [match.start() for match in re.finditer(pattern, module_data)]
    alloc = pm.allocate(100)

    count = 0
    for start in matches:
        addr = fir + start
        hp_addr = pm.read_longlong(pm.read_longlong(addr + 0x190)) + 0x138
        coords = pm.read_longlong(pm.read_longlong(addr + 0x190) + 0x68) + 0x70

        if pm.read_bytes(addr + 0x6C, 1) == b"\x06" and pm.read_int(hp_addr) >= 100:
            Funcs.spawn_enemy_to_coords(
                pm, address_list, 2120, pm.read_bytes(coords, 12), alloc
            )
            # p(addr)
            count += 1
            pm.start_thread(alloc)
            # print(pm.read_int(hp_addr))
            # pm.write_int(hp_addr, 0)
    print("--- %s seconds ---" % (time() - start_time))
    print(count)


if __name__ != "__main__":
    pm = pymem.Pymem("eldenring.exe")
