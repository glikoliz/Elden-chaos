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
    get_addr_from_list
)


class Funcs:
    def disable_fast_travel()->None:
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )

    def enable_fast_travel()->None:  # TODO:can be better
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x00\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11,
        )

    def warp_to(grace_id: int)->None:
        warp_func = pm.allocate(100)
        cs_lua_event = get_cs_lua_event(pm).to_bytes(8, byteorder="little")
        lua_warp = get_lua_warp(pm).to_bytes(8, byteorder="little")
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
        pm.write_int(warp_loc, grace_id)
        pm.start_thread(warp_func)

        pm.free(warp_func)

    def wait(wait_time: int)->None:
        sleep(wait_time)
        cutscene_on = get_addr_from_list(pm, addr_list['CUTSCENE_ON'])
        while pm.read_int(cutscene_on) != 0:
            sleep(0.2)

    def change_model_size(addr: int, x: float, y: float, z: float)->None:
        pm.write_float(addr, x)
        pm.write_float(addr + 4, y)
        pm.write_float(addr + 8, z)

    def respawn_boss(boss_addr: int)->None:
        pm.write_uchar(boss_addr, 0)

    def spawn_enemy(id: int) -> None:  # TODO:chr_count may be broken
        pm.write_bytes(
            get_addr_from_list(pm, addr_list['SPAWN_NPC_X']), pm.read_bytes(get_addr_from_list(pm,addr_list['CURRENT_POS']), 12), 12
        )  # WRITE CURRENT POS

        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        chr_id_addr=get_addr_from_list(pm, addr_list['CHR_ID'])
        # chr_id_addr = get_address_with_offsets(pm, worldchrman, addr_list["CHR_ID"][1])
        # print(hex(chr_id_addr))
        pm.write_bytes(chr_id_addr, chr_id, len(chr_id))
        pm.write_int(chr_id_addr - 0x10, id * 10000)  # NPC_PARAM_ID
        pm.write_int(chr_id_addr - 0x0C, id * 10000)  # NPC_THINK_PARAM_ID
        pm.write_int(chr_id_addr - 0x08, 0)  # EVENT_ENTITY_ID
        pm.write_int(chr_id_addr - 0x04, 0)  # TALK_ID
        pm.write_bytes(chr_id_addr + 0x78, b"\x00", 1)  # NPC_ENEMY_TYPE
        
        worldchrman_addr = get_worldchrman(pm)
        spawned_enemy = get_spawn_addr(pm, worldchrman_addr).to_bytes(
            8, byteorder="little"
        )
        
        assembly_code = (
            b"\x48\xA1"
            + worldchrman_addr.to_bytes(8, byteorder="little")
            + b"\x48\x8B\x80\x40\xE6\x01\x00"
            b"\xC6\x40\x44\x01"
            b"\x8B\x15\x30\x00\x00\x00"
            b"\x6B\xD2\x10"
            b"\x48\xBB" + spawned_enemy + b"\x48\x01\xD3"
            b"\x8A\x80\x78\x01\x00\x00"
            b"\x88\x43\x0B"
            b"\xFF\x05\x11\x00\x00\x00"
            b"\xC3"
        )
        l = pm.allocate(100)
        pm.write_bytes(l, assembly_code, len(assembly_code))
        pm.start_thread(l)
        pm.free(l)


if __name__ != "__main__":
    pm = Pymem("eldenring.exe")
    with open("lib/addresses.json", "r") as file:
        json_data = json.load(file)
    addr_list = {}
    for obj in json_data:
        name = obj["name"]
        addr_list[name] = [
            obj["addr"],
            [int(element, 16) for element in obj["offsets"].split()],
        ]
