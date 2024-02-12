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
    get_field_area
)


class Funcs:

    def disable_fast_travel() -> None:
        fieldarea = pm.read_longlong(get_field_area(pm))+0xA0
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )
        pm.write_int(fieldarea, 1)

    def enable_fast_travel() -> None:
        fieldarea = pm.read_longlong(get_field_area(pm))+0xA0
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\x90\x90\x90\x90\x90\x89\x9E\xA0\x00\x00\x00",
            11,
        )
        pm.write_int(fieldarea, 0)

    def warp_to(grace_id: int) -> None:
        warp_func = pm.allocate(100)
        cs_lua_event = get_cs_lua_event(pm).to_bytes(8, byteorder="little")
        lua_warp = get_lua_warp(pm).to_bytes(8, byteorder="little")
        bytecode = (b"\x48\x83\xEC\x48"
                    b"\x48\xB8" + cs_lua_event + b"\x48\x8B\x48\x18"
                    b"\x48\x8B\x50\x08"
                    b"\x8B\x05\x1C\x00\x00\x00"
                    b"\x44\x8D\x80\x18\xFC\xFF\xFF\xFF\x15\x02\x00\x00\x00"
                    b"\xEB\x08" + lua_warp + b"\x48\x83\xC4\x48"
                    b"\xC3")
        warp_loc = warp_func + len(bytecode)
        # addr=pm.allocate(len(bytecode))
        pm.write_bytes(warp_func, bytecode, len(bytecode))
        pm.write_int(warp_loc, grace_id)
        pm.start_thread(warp_func)

        pm.free(warp_func)

    def wait(wait_time: int) -> int:
        cutscene_on = get_addr_from_list(pm, addr_list["CUTSCENE_ON"])
        for i in range(wait_time):
            sleep(1)
            if (pm.read_int(cutscene_on) != 0):
                return wait_time-i
        return -1

    def is_player_in_cutscene() -> bool:
        cutscene_on = get_addr_from_list(pm, addr_list["CUTSCENE_ON"])
        return pm.read_int(cutscene_on) != 0

    def change_model_size(addr: int, x: float, y: float, z: float) -> None:
        pm.write_float(addr, x)
        pm.write_float(addr + 4, y)
        pm.write_float(addr + 8, z)

    def respawn_boss(boss_addr: int) -> None:
        pm.write_uchar(boss_addr, 0)

    def spawn_enemy(id: int) -> None:  # TODO:chr_count may be broken
        pm.write_bytes(
            get_addr_from_list(pm, addr_list["SPAWN_NPC_X"]),
            pm.read_bytes(get_addr_from_list(pm, addr_list["CURRENT_POS"]),
                          12),
            12,
        )  # WRITE CURRENT POS

        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        chr_id_addr = get_addr_from_list(pm, addr_list["CHR_ID"])

        pm.write_bytes(chr_id_addr, chr_id, len(chr_id))
        pm.write_int(chr_id_addr - 0x10, id * 10000)  # NPC_PARAM_ID
        pm.write_int(chr_id_addr - 0x0C, id * 10000)  # NPC_THINK_PARAM_ID
        pm.write_int(chr_id_addr - 0x08, 0)  # EVENT_ENTITY_ID
        pm.write_int(chr_id_addr - 0x04, 0)  # TALK_ID
        pm.write_bytes(chr_id_addr + 0x78, b"\x00", 1)  # NPC_ENEMY_TYPE

        worldchrman_addr = get_worldchrman(pm)
        spawned_enemy = get_spawn_addr(pm, worldchrman_addr).to_bytes(
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
        l = pm.allocate(100)
        pm.write_bytes(l, assembly_code, len(assembly_code))
        pm.start_thread(l)
        pm.free(l)

    def hide_cloth():
        inject = b"\xE9\x45\xC0\xAC\xFE"
        code = b"\x90\x90\x90\x90\x90\xE9\xB1\x3F\x53\x01\xF3\x41\x0F\x10\x08\xE9\xA7\x3F\x53\x01"
        pm.write_bytes(pm.base_address + 0x500, code, len(code))
        pm.write_bytes(pm.base_address + 0x15344B6, inject, len(inject))
        pass

    def show_cloth():
        inject = b"\xF3\x41\x0F\x10\x08"
        code = b"\x90\x90\x90\x90\x90\xE9\xB1\x3F\x53\x01\xF3\x41\x0F\x10\x08\xE9\xA7\x3F\x53\x01"
        pm.write_bytes(pm.base_address + 0x500, b"\x00" * len(code), len(code))
        pm.write_bytes(pm.base_address + 0x15344B6, inject, len(inject))

    def get_closest_enemy(player_coords: int):
        chr_count, chrset = get_chr_count_and_set(pm)
        min_distance = [-1, 10000]  # addr, distance
        player_x, player_y, player_z = (
            pm.read_float(player_coords),
            pm.read_float(player_coords + 0x04),
            pm.read_float(player_coords + 0x08),
        )
        for i in range(1, chr_count):
            enemy_addr = pm.read_longlong(chrset + i * 0x10)
            if enemy_addr:
                alliance = get_address_with_offsets(pm, enemy_addr, [0x6C])
                if pm.read_bytes(alliance, 1) == b"\x06":
                    coords = (get_address_with_offsets(
                        pm, enemy_addr, [0x190, 0x68, 0x0]) + 0x70)
                    x, y, z = (
                        pm.read_float(coords),
                        pm.read_float(coords + 0x04),
                        pm.read_float(coords + 0x08),
                    )
                    distance = ((player_x - x)**2 + (player_y - y)**2 +
                                (player_z - z)**2)**(1 / 2)
                    if min_distance[1] > distance:
                        min_distance = [coords, distance]
        dungeon_count, dungeon_chrset = get_dungeon_chr_count_and_set(pm)
        for i in range(1, dungeon_count):
            enemyins = pm.read_longlong(dungeon_chrset + i * 0x10)
            if enemyins:
                alliance = get_address_with_offsets(pm, enemyins, [0x6C])
                if pm.read_bytes(alliance, 1) == b"\x06":
                    coords = (get_address_with_offsets(
                        pm, enemyins, [0x190, 0x68, 0x0]) + 0x70)
                    x, y, z = (
                        pm.read_float(coords),
                        pm.read_float(coords + 0x04),
                        pm.read_float(coords + 0x08),
                    )
                    distance = ((player_x - x)**2 + (player_y - y)**2 +
                                (player_z - z)**2)**(1 / 2)
                    if min_distance[1] > distance:
                        min_distance = [coords, distance]
        return min_distance


if __name__ != "__main__":
    pm = Pymem("eldenring.exe")
    with open("resources/addresses.json", "r") as file:
        json_data = json.load(file)
    addr_list = {}
    for obj in json_data:
        name = obj["name"]
        addr_list[name] = [
            obj["addr"],
            [int(element, 16) for element in obj["offsets"].split()],
        ]
