from time import sleep
import json
from pymem import Pymem
from lib.getaddress import (
    get_address_with_offsets,
    get_eventflagman,
    get_cs_lua_event,
    get_lua_warp,
    get_worldchrman,
    get_spawn_addr,
    get_addr_from_list,
    get_dungeon_chr_count_and_set,
    get_chr_count_and_set,
    get_field_area)


class Funcs:
    def __init__(self) -> None:
        self.pm = Pymem('eldenring.exe')

    def disable_fast_travel(self) -> None:
        fieldarea = self.pm.read_longlong(get_field_area(self.pm))+0xA0
        self.pm.write_bytes(
            self.pm.base_address + 0x61F232,
            b"\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )
        self.pm.write_int(fieldarea, 1)

    def enable_fast_travel(self) -> None:
        fieldarea = self.pm.read_longlong(get_field_area(self.pm))+0xA0
        self.pm.write_bytes(
            self.pm.base_address + 0x61F232,
            b"\x90\x90\x90\x90\x90\x89\x9E\xA0\x00\x00\x00",
            11,
        )
        self.pm.write_int(fieldarea, 0)

    def warp_to(self, grace_id: int) -> None:
        warp_func = self.pm.allocate(100)
        cs_lua_event = get_cs_lua_event(
            self.pm).to_bytes(8, byteorder="little")
        lua_warp = get_lua_warp(self.pm).to_bytes(8, byteorder="little")
        bytecode = (b"\x48\x83\xEC\x48"
                    b"\x48\xB8" + cs_lua_event + b"\x48\x8B\x48\x18"
                    b"\x48\x8B\x50\x08"
                    b"\x8B\x05\x1C\x00\x00\x00"
                    b"\x44\x8D\x80\x18\xFC\xFF\xFF\xFF\x15\x02\x00\x00\x00"
                    b"\xEB\x08" + lua_warp + b"\x48\x83\xC4\x48"
                    b"\xC3")
        warp_loc = warp_func + len(bytecode)
        # addr=self.pm.allocate(len(bytecode))
        self.pm.write_bytes(warp_func, bytecode, len(bytecode))
        self.pm.write_int(warp_loc, grace_id)
        self.pm.start_thread(warp_func)

        self.pm.free(warp_func)

    def wait(self, wait_time: int) -> int:
        cutscene_on = get_addr_from_list(self.pm, addr_list["CUTSCENE_ON"])
        for i in range(wait_time):
            sleep(1)
            if (self.pm.read_int(cutscene_on) != 0):
                return wait_time-i
        return -1

    def is_player_in_cutscene(self) -> bool:
        cutscene_on = get_addr_from_list(self.pm, addr_list["CUTSCENE_ON"])
        return self.pm.read_int(cutscene_on) != 0

    def change_model_size(self, addr: int, x: float, y: float, z: float) -> None:
        self.pm.write_float(addr, x)
        self.pm.write_float(addr + 4, y)
        self.pm.write_float(addr + 8, z)

    def respawn_boss(self, boss_addr: int) -> None:
        self.pm.write_uchar(boss_addr, 0)

    def spawn_enemy(self, id: int) -> None:
        self.pm.write_bytes(
            get_addr_from_list(self.pm, addr_list["SPAWN_NPC_X"]),
            self.pm.read_bytes(get_addr_from_list(self.pm, addr_list["CURRENT_POS"]),
                               12),
            12,
        )  # WRITE CURRENT POS

        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        chr_id_addr = get_addr_from_list(self.pm, addr_list["CHR_ID"])

        self.pm.write_bytes(chr_id_addr, chr_id, len(chr_id))
        self.pm.write_int(chr_id_addr - 0x10, id * 10000)  # NPC_PARAM_ID
        self.pm.write_int(chr_id_addr - 0x0C, id * 10000)  # NPC_THINK_PARAM_ID
        self.pm.write_int(chr_id_addr - 0x08, 0)  # EVENT_ENTITY_ID
        self.pm.write_int(chr_id_addr - 0x04, 0)  # TALK_ID
        self.pm.write_bytes(chr_id_addr + 0x78, b"\x00", 1)  # NPC_ENEMY_TYPE

        worldchrman_addr = get_worldchrman(self.pm)
        spawned_enemy = get_spawn_addr(self.pm, worldchrman_addr).to_bytes(
            8, byteorder="little")

        assembly_code = (b"\x48\xA1" +
                         worldchrman_addr.to_bytes(8, byteorder="little") +
                         b"\x48\x8B\x80\x40\xE6\x01\x00"
                         b"\xC6\x40\x44\x01"
                         b"\x8B\x15\x30\x00\x00\x00"
                         b"\x6B\xD2\x10"
                         b"\x48\xBB" + spawned_enemy + b"\x48\x01\xD3"
                         b"\x8A\x80\x78\x01\x00\x00"
                         b"\x88\x43\x0B"
                         b"\xFF\x05\x11\x00\x00\x00"
                         b"\xC3")
        l = self.pm.allocate(100)
        self.pm.write_bytes(l, assembly_code, len(assembly_code))
        self.pm.start_thread(l)
        self.pm.free(l)

    def hide_cloth(self):
        inject = b"\xE9\x45\xC0\xAC\xFE"
        code = b"\x90\x90\x90\x90\x90\xE9\xB1\x3F\x53\x01\xF3\x41\x0F\x10\x08\xE9\xA7\x3F\x53\x01"
        self.pm.write_bytes(self.pm.base_address + 0x500, code, len(code))
        self.pm.write_bytes(self.pm.base_address +
                            0x15344B6, inject, len(inject))
        pass

    def show_cloth(self):
        inject = b"\xF3\x41\x0F\x10\x08"
        code = b"\x90\x90\x90\x90\x90\xE9\xB1\x3F\x53\x01\xF3\x41\x0F\x10\x08\xE9\xA7\x3F\x53\x01"
        self.pm.write_bytes(self.pm.base_address + 0x500,
                            b"\x00" * len(code), len(code))
        self.pm.write_bytes(self.pm.base_address +
                            0x15344B6, inject, len(inject))

    def get_closest_enemy(self, player_coords: int):
        chr_count, chrset = get_chr_count_and_set(self.pm)
        res_addr = -1
        res_distance = 10000
        player_x, player_y, player_z = (
            self.pm.read_float(player_coords),
            self.pm.read_float(player_coords + 0x04),
            self.pm.read_float(player_coords + 0x08),
        )
        for i in range(1, chr_count):
            enemy_addr = self.pm.read_longlong(chrset + i * 0x10)
            if enemy_addr:
                alliance = get_address_with_offsets(
                    self.pm, enemy_addr, [0x6C])
                if self.pm.read_bytes(alliance, 1) == b"\x06":
                    coords = (get_address_with_offsets(
                        self.pm, enemy_addr, [0x190, 0x68, 0x0]) + 0x70)
                    x, y, z = (
                        self.pm.read_float(coords),
                        self.pm.read_float(coords + 0x04),
                        self.pm.read_float(coords + 0x08),
                    )
                    distance = ((player_x - x)**2 + (player_y - y)**2 +
                                (player_z - z)**2)**(1 / 2)
                    
                    if res_distance > distance:
                        res_addr = coords
                        res_distance = distance
        dungeon_count, dungeon_chrset = get_dungeon_chr_count_and_set(self.pm)
        for i in range(1, dungeon_count):
            enemyins = self.pm.read_longlong(dungeon_chrset + i * 0x10)
            if enemyins:
                alliance = get_address_with_offsets(self.pm, enemyins, [0x6C])
                if self.pm.read_bytes(alliance, 1) == b"\x06":
                    coords = (get_address_with_offsets(
                        self.pm, enemyins, [0x190, 0x68, 0x0]) + 0x70)
                    x, y, z = (
                        self.pm.read_float(coords),
                        self.pm.read_float(coords + 0x04),
                        self.pm.read_float(coords + 0x08),
                    )
                    distance = ((player_x - x)**2 + (player_y - y)**2 +
                                (player_z - z)**2)**(1 / 2)
                    if res_distance > distance:
                        res_addr = coords
                        res_distance = distance
        return [res_addr, res_distance]

    def is_lvl_okay(self):
        lvl_addr = get_addr_from_list(self.pm, addr_list['CHR_LEVEL'])
        attr_addr = get_addr_from_list(self.pm, addr_list['STATS'])
        current_lvl = -79  # default level
        for i in range(8):
            current_lvl += self.pm.read_int(attr_addr + 4 * i)
        return current_lvl == self.pm.read_int(lvl_addr)

    def set_max_hp_fp(self):
        hp_addr = get_addr_from_list(self.pm, addr_list['HP'])
        max_hp = self.pm.read_int(
            get_addr_from_list(self.pm, addr_list['MAX_HP']))
        fp_addr = get_addr_from_list(self.pm, addr_list['FP'])
        max_fp = self.pm.read_int(
            get_addr_from_list(self.pm, addr_list['MAX_FP']))
        self.pm.write_int(hp_addr, max_hp)
        self.pm.write_int(fp_addr, max_fp)


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
