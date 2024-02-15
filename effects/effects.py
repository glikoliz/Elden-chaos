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
    get_flask,
    get_list_of_nearby_npcs,
)
import json
import logging

logging.basicConfig(
    filename="logfile.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


class Effect:
    def __init__(self) -> None:
        self.pm = pymem.Pymem("eldenring.exe")
        self.funcs = Funcs()

    def onStart(self):
        pass

    def onStop(self):
        pass

    def onTick(self):
        return -1


class OHKO(Effect):
    def onStart(self):
        try:
            self.basehp_addr = get_addr_from_list(self.pm, addr_list["MAX_HP"])
            self.basehp = self.pm.read_int(self.basehp_addr)
            self.pm.write_int(self.basehp_addr, 1)
            return 0
        except Exception as e:
            logging.exception(e)

    def onStop(self):
        try:
            if self.pm.read_int(self.basehp_addr) == 1:
                self.pm.write_int(self.basehp_addr, self.basehp)
        except Exception as e:
            logging.exception(e)


class MANA_LEAK(Effect):
    def onStart(self):
        try:
            self.fp_addr = get_addr_from_list(self.pm, addr_list["FP"])
            self.minus_fp = self.pm.read_int(self.fp_addr) // 20
        except Exception as e:
            logging.exception(e)

    def onTick(self):
        try:
            fp = self.pm.read_int(self.fp_addr)
            if fp >= self.minus_fp and not self.funcs.is_player_in_cutscene():
                self.pm.write_int(self.fp_addr, fp - self.minus_fp)
                return 0
            else:
                return -1
        except:
            return -1


class DISABLE_GRAVITY(Effect):
    def onStart(self):
        try:
            self.current_animation_addr = get_addr_from_list(
                self.pm, addr_list["CURRENT_ANIMATION"])
            self.animation_addr = get_addr_from_list(self.pm,
                                                     addr_list["ANIMATION"])

            self.pm.write_bytes(
                get_addr_from_list(self.pm, addr_list["DISABLE_GRAVITY"]),
                b"\x01", 1)
        except Exception as e:
            logging.exception(e)

    def onTick(self):
        try:
            if self.pm.read_int(self.current_animation_addr) in [
                    10202000,
                    10202040,
                    23033030,
                    23033060,
            ]:
                self.pm.write_int(self.animation_addr, 0)
        except Exception as e:
            logging.exception(e)

    def onStop(self):
        try:
            self.pm.write_bytes(
                get_addr_from_list(self.pm, addr_list["DISABLE_GRAVITY"]),
                b"\x00", 1)
        except Exception as e:
            logging.exception(e)


class WARP_TO_RANDOM_GRACE(Effect):
    def onStart(self):
        try:
            random_number = int(
                getline("resources/graces.txt", randint(0, 305)).strip())
            self.funcs.wait(0)
            self.funcs.warp_to(random_number)
        except:
            pass


class GODRICK_TIME(Effect):
    def onStart(self):
        try:
            self.godrick_addr = get_addr_from_list(self.pm,
                                                   addr_list["GODRICK"])
            self.cutscene_on = get_addr_from_list(self.pm,
                                                  addr_list["CUTSCENE_ON"])
            self.funcs.respawn_boss(self.godrick_addr)
            self.funcs.disable_fast_travel()
            self.funcs.warp_to(18002950)
            self.funcs.wait(3)
        except Exception as e:
            logging.exception(e)

    def onTick(self):
        if (self.pm.read_uchar(self.godrick_addr) == 0
                and self.pm.read_int(self.cutscene_on) == 0):
            return 0
        return -1

    def onStop(self):
        self.funcs.enable_fast_travel()


class SPAWN_MALENIA(Effect):
    def onStart(self):
        self.funcs.spawn_enemy(2120)


class GO_REST(Effect):
    def onStart(self):
        self.pm.write_float(
            get_addr_from_list(self.pm, addr_list["ANIMATION_SPEED"]), 0.0)
        self.invincible = INVINCIBILITY()
        self.invincible.onStart()

    def onStop(self):
        self.pm.write_float(
            get_addr_from_list(self.pm, addr_list["ANIMATION_SPEED"]), 1.0)
        self.invincible.onStop()


class INVINCIBILITY(Effect):
    def onStart(self):
        self.old_flags = self.pm.read_bytes(
            get_addr_from_list(self.pm, addr_list["NO_DEAD"]), 1)[0]
        self.new_flags = self.old_flags | 0b00011
        self.pm.write_bytes(get_addr_from_list(self.pm, addr_list["NO_DEAD"]),
                            bytes([self.new_flags]), 1)

    def onStop(self):
        self.pm.write_bytes(get_addr_from_list(self.pm, addr_list["NO_DEAD"]),
                            bytes([self.old_flags]), 1)


class INVISIBILITY(Effect):
    def onStart(self):
        chr_dbg_flags = get_chr_dbg_flags(self.pm)
        self.pm.write_bytes(chr_dbg_flags + 8, b"\x01", 1)  # hide player
        self.pm.write_bytes(chr_dbg_flags + 9, b"\x01", 1)  # silence player

    def onStop(self):
        chr_dbg_flags = get_chr_dbg_flags(self.pm)
        self.pm.write_bytes(chr_dbg_flags + 8, b"\x00", 1)
        self.pm.write_bytes(chr_dbg_flags + 9, b"\x00", 1)


class GHOST(Effect):
    def onStart(self):
        self.pm.write_int(get_addr_from_list(
            self.pm, addr_list["CHR_MODEL"]), 3)

    def onStop(self):
        self.pm.write_int(get_addr_from_list(
            self.pm, addr_list["CHR_MODEL"]), 0)


class POOR_TARNISHED(Effect):
    def onStart(self):
        self.pm.write_int(get_addr_from_list(self.pm, addr_list["RUNES"]), 0)


class RICH_TARNISHED(Effect):
    def onStart(self):
        runes_addr = get_addr_from_list(self.pm, addr_list["RUNES"])
        total_runes = self.pm.read_int(
            get_addr_from_list(self.pm, addr_list["TOTAL_RUNES"]))
        self.pm.write_int(runes_addr, self.pm.read_int(
            runes_addr) + total_runes // 10)


class CHANGE_GENDER(Effect):
    def onStart(self):
        gender_addr = get_addr_from_list(self.pm, addr_list["GENDER"])
        if self.pm.read_bytes(gender_addr, 1) == b"\x01":
            self.pm.write_bytes(gender_addr, b"\x00", 1)
        else:
            self.pm.write_bytes(gender_addr, b"\x01", 1)


class RANDOM_STATS(Effect):
    def onStart(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        while not self.funcs.is_lvl_okay():
            sleep(0.5)
        self.current_stats = self.pm.read_bytes(addr, 32)
        for i in range(8):
            self.pm.write_int(addr + 4 * i, randint(1, 99))
        self.funcs.set_max_hp_fp()
        
    def onStop(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        if not self.funcs.is_lvl_okay():
            self.pm.write_bytes(addr, self.current_stats, 32)
            self.funcs.set_max_hp_fp()  


class SONIC_SPEED(Effect):
    def onStart(self):
        self.pm.write_float(get_addr_from_list(
            self.pm, addr_list["ANIMATION_SPEED"]), 3.0)

    def onStop(self):
        self.pm.write_float(get_addr_from_list(
            self.pm, addr_list["ANIMATION_SPEED"]), 1.0)


class SLOW_CHR(Effect):
    def onStart(self):
        self.pm.write_float(get_addr_from_list(
            self.pm, addr_list["ANIMATION_SPEED"]), 0.3)

    def onStop(self):
        self.pm.write_float(get_addr_from_list(
            self.pm, addr_list["ANIMATION_SPEED"]), 1.0)


class FULL_STAMINA(Effect):
    def onStart(self):
        chr_dbg_flags = get_chr_dbg_flags(self.pm)
        self.pm.write_bytes(chr_dbg_flags + 4, b"\x01", 1)

    def onStop(self):
        chr_dbg_flags = get_chr_dbg_flags(self.pm)
        self.pm.write_bytes(chr_dbg_flags + 4, b"\x00", 1)


class LVL1_CROOK(Effect):
    def onStart(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        while not self.funcs.is_lvl_okay():
            sleep(0.5)
        hp_addr = get_addr_from_list(self.pm, addr_list["HP"])
        fp_addr = get_addr_from_list(self.pm, addr_list["FP"])

        self.current_stats = self.pm.read_bytes(addr, 32)
        self.hp, self.fp = self.pm.read_int(hp_addr), self.pm.read_int(fp_addr)
        for i in range(8):
            self.pm.write_int(addr + 4 * i, 1)

    def onStop(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        hp_addr = get_addr_from_list(self.pm, addr_list["HP"])
        fp_addr = get_addr_from_list(self.pm, addr_list["FP"])
        if not self.funcs.is_lvl_okay():
            self.pm.write_bytes(addr, self.current_stats, 32)
            self.pm.write_int(hp_addr, self.hp)
            self.pm.write_int(fp_addr, self.fp)


class LVL99_BOSS(Effect):  # TODO: check if stats matches lvl
    def onStart(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        while not self.funcs.is_lvl_okay():
            sleep(0.5)
        self.current_stats = self.pm.read_bytes(addr, 32)
        for i in range(8):
            self.pm.write_int(addr + 4 * i, 99)
        self.funcs.set_max_hp_fp()

    def onStop(self):
        addr = get_addr_from_list(self.pm, addr_list["STATS"])
        if not self.funcs.is_lvl_okay():
            self.pm.write_bytes(addr, self.current_stats, 32)


class DWARF_MODE(Effect):
    def onStart(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        self.funcs.hide_cloth()
        self.funcs.change_model_size(chr_size_addr, 0.3, 0.3, 0.3)

    def onStop(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        if (self.pm.read_bytes(chr_size_addr, 12) == b'\x9A\x99\x99\x3E\x9A\x99\x99\x3E\x9A\x99\x99\x3E'):
            self.funcs.change_model_size(chr_size_addr, 1.0, 1.0, 1.0)
            self.funcs.show_cloth()


class BIG_BOY(Effect):
    def onStart(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        self.funcs.hide_cloth()
        self.funcs.change_model_size(chr_size_addr, 2.0, 2.0, 2.0)

    def onStop(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        if (self.pm.read_bytes(chr_size_addr, 12) == b'\x00\x00\x00\x40\x00\x00\x00\x40\x00\x00\x00\x40'):
            self.funcs.change_model_size(chr_size_addr, 1.0, 1.0, 1.0)
            self.funcs.show_cloth()


class RANDOM_MODEL_SIZE(Effect):
    def onStart(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        self.funcs.hide_cloth()
        self.funcs.change_model_size(
            chr_size_addr,
            uniform(0.1, 2.5),
            uniform(0.1, 2.5),
            uniform(0.1, 2.5),
        )

    def onStop(self):
        chr_size_addr = get_addr_from_list(self.pm, addr_list["CHR_SIZE"])
        if (self.pm.read_bytes(chr_size_addr, 12) != b'\x00\x00\x80\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F'):
            self.funcs.change_model_size(chr_size_addr, 1.0, 1.0, 1.0)
            self.funcs.show_cloth()


class HUSSEIN(Effect):
    def onStart(self):
        animation = get_addr_from_list(self.pm, addr_list["ANIMATION"])
        animation_speed = get_addr_from_list(
            self.pm, addr_list["ANIMATION_SPEED"])
        chr_model = get_addr_from_list(self.pm, addr_list["CHR_MODEL"])

        self.pm.write_int(animation, 67011)
        self.pm.write_float(animation_speed, 15.0)
        self.pm.write_int(chr_model, 2)
        sleep(0.3)
        self.pm.write_float(animation_speed, 1.0)

    def onStop(self):
        animation = get_addr_from_list(self.pm, addr_list["ANIMATION"])
        chr_model = get_addr_from_list(self.pm, addr_list["CHR_MODEL"])

        self.pm.write_int(animation, 0)
        self.pm.write_int(chr_model, 0)


class BUFF(Effect):
    pass
    # addr = address_list["CHR_SIZE"]
    # self.pm.write_int(address_list["ANIMATION"], 60470)
    # sleep(6)
    # Funcs.change_model_size(self.pm, addr, 1.7, 1.7, 1.7)
    # self.pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x01", 1)
    # self.pm.write_int(address_list["ANIMATION"], 60471)
    # sleep(10)
    # Funcs.change_model_size(self.pm, addr, 1.0, 1.0, 1.0)
    # self.pm.write_bytes(address_list["CHR_DBG_FLAGS"] + 2, b"\x00", 1)


class CYBERPUNK_EXPERIENCE(Effect):
    def onStart(self):
        self.collision_addr = self.pm.pattern_scan_module(
            b"\xC6\x83\x78\x0D\x00\x00\xFF", "eldenring.exe"
        )
        self.pm.write_bytes(self.collision_addr,
                            b"\xC6\x83\x78\x0D\x00\x00\x02", 7)
        self.pm.write_float(get_addr_from_list(
            self.pm, addr_list["FPS"]), 20.0)
        self.pm.write_bytes(get_addr_from_list(
            self.pm, addr_list["USE_FPS"]), b"\x01", 1)
        self.pm.write_int(get_addr_from_list(
            self.pm, addr_list["ANIMATION"]), 60265)
        sleep(1.5)
        self.pm.write_int(get_addr_from_list(
            self.pm, addr_list["ANIMATION"]), 0)

    def onStop(self):
        self.pm.write_bytes(get_addr_from_list(
            self.pm, addr_list["USE_FPS"]), b"\x00", 1)
        self.pm.write_bytes(self.collision_addr,
                            b"\xC6\x83\x78\x0D\x00\x00\xFF", 7)


class SPEED_EVERYONE(Effect):
    def onStart(self):
        self.funcs.wait(0)
        addr_list = get_list_of_nearby_npcs(self.pm)
        for addr in addr_list:
            try:
                speed = get_address_with_offsets(
                    self.pm, addr, [0x190, 0x28, 0x17C8])
                self.pm.write_float(speed, 2.0)
            except Exception as e:
                logging.exception(e)

    def onStop(self):
        self.funcs.wait(0)
        addr_list = get_list_of_nearby_npcs(self.pm)
        for addr in addr_list:
            try:
                speed = get_address_with_offsets(
                    self.pm, addr, [0x190, 0x28, 0x17C8])
                if (self.pm.read_float(speed) == 2.0):
                    self.pm.write_float(speed, 1.0)
            except Exception as e:
                logging.exception(e)


class SLOW_EVERYONE(Effect):
    def onStart(self):
        self.funcs.wait(0)
        addr_list = get_list_of_nearby_npcs(self.pm)
        for addr in addr_list:
            try:
                speed = get_address_with_offsets(
                    self.pm, addr, [0x190, 0x28, 0x17C8])
                self.pm.write_float(speed, 0.3)
            except Exception as e:
                logging.exception(e)

    def onStop(self):
        self.funcs.wait(0)
        addr_list = get_list_of_nearby_npcs(self.pm)
        for addr in addr_list:
            try:
                speed = get_address_with_offsets(
                    self.pm, addr, [0x190, 0x28, 0x17C8])
                if (self.pm.read_float(speed) == 0.3):
                    self.pm.write_float(speed, 1.0)
            except Exception as e:
                logging.exception(e)


class TP_EVERYONE_TO_PLAYER(Effect):
    def onStart(self):
        current_pos_addr = get_addr_from_list(
            self.pm, addr_list["CURRENT_POS"])
        chr_count, chrset = get_chr_count_and_set(self.pm)
        for i in range(1, chr_count):
            enemy_addr = self.pm.read_longlong(chrset + i * 0x10)
            if enemy_addr:
                try:
                    if self.pm.read_bytes(enemy_addr+0x6C, 1) == b"\x06":
                        coords = (
                            get_address_with_offsets(
                                self.pm, enemy_addr, [0x190, 0x68, 0x0])
                            + 0x70
                        )
                        self.pm.write_bytes(coords, self.pm.read_bytes(
                            current_pos_addr, 12), 12)
                except Exception as e:
                    logging.exception(e)


class TP_PLAYER_TO_NEARBY_ENEMY(Effect):
    def onStart(self):
        player_coords = get_addr_from_list(
            self.pm, ["worldchrman", [124168, 400, 104, 112]])
        min_distance = self.funcs.get_closest_enemy(player_coords)
        self.pm.write_bytes(
            player_coords, self.pm.read_bytes(min_distance[0], 12), 12)


class ONE_FLASK(Effect):
    def onStart(self):
        crimson_flask = get_flask(self.pm)
        self.pm.write_bytes(crimson_flask, b'\x01', 1)


if __name__ != "__main__":
    with open("resources/addresses.json", "r") as file:
        json_data = json.load(file)
    addr_list = {}
    for obj in json_data:
        name = obj["name"]
        addr_list[name] = [
            obj["addr"],
            [int(element, 16) for element in obj["offsets"].split()],
        ]
