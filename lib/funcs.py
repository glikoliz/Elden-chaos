from time import sleep
class Funcs:
    def disable_fast_travel(pm):
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11
        )

    def enable_fast_travel(pm):  # TODO:can be better
        pm.write_bytes(
            pm.base_address + 0x61F232,
            b"\xBB\x00\x00\x00\x00\x89\x9E\xA0\x00\x00\x00",
            11
        )

    def warp_to(pm, address_list, grace):
        warp_func = pm.allocate(100)
        cs_lua_event = address_list["CS_LUA_EVENT"].to_bytes(8, byteorder="little")
        lua_warp = address_list["LUA_WARP"].to_bytes(8, byteorder="little")
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

    def wait(pm, address_list, wait_time):
        sleep(wait_time)
        while pm.read_int(address_list["CUTSCENE_ON"]) != 0:
            sleep(0.1)

    def change_model_size(pm, addr, x, y, z):
        pm.write_float(addr, x)
        pm.write_float(addr + 4, y)
        pm.write_float(addr + 8, z)

    def respawn_boss(pm, boss_addr):
        pm.write_uchar(boss_addr, 0)

    def spawn_enemy(pm, address_list, id):  # TODO:chr_count may be broken
        pm.write_bytes(
            address_list["SPAWN_NPC_X"], pm.read_bytes(address_list["CURRENT_POS"], 12), 12
        )  # WRITE CURRENT POS

        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        pm.write_bytes(address_list["CHR_ID"], chr_id, len(chr_id))
        pm.write_int(address_list["NPC_PARAM_ID"], id * 10000)
        pm.write_int(address_list["NPC_THINK_PARAM_ID"], id * 10000)
        pm.write_int(address_list["EVENT_ENTITY_ID"], 0)
        pm.write_int(address_list["TALK_ID"], 0)
        pm.write_bytes(address_list["NPC_ENEMY_TYPE"], b"\x00", 1)
        # WRITE CHR INFO #
        spawned_enemy = address_list["SPAWN_ADDR"].to_bytes(8, byteorder="little")
        worldchrman = address_list["WORLDCHRMAN"].to_bytes(8, byteorder="little")
        assembly_code = (
            b"\x48\xA1" + worldchrman + b"\x48\x8B\x80\x40\xE6\x01\x00"
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
        # print(format(l,'X'))
        pm.write_bytes(l, assembly_code, len(assembly_code))
        pm.start_thread(l)
        # print(pm.read_int(l+0x4B))
        pm.free(l)

    def spawn_enemy_to_coords(
        pm, address_list, id, coords, allocate_mem
    ):  # TODO:chr_count may be broken
        pm.write_bytes(address_list["SPAWN_NPC_X"], coords, 12)  # WRITE CURRENT POS
        print(hex(address_list["SPAWN_NPC_X"]))
        # WRITE CHR INFO #
        chr_id = ("c" + str(id)).encode("utf-16le")
        pm.write_bytes(address_list["CHR_ID"], chr_id, len(chr_id))
        pm.write_int(address_list["NPC_PARAM_ID"], id * 10000)
        pm.write_int(address_list["NPC_THINK_PARAM_ID"], id * 10000)
        pm.write_int(address_list["EVENT_ENTITY_ID"], 0)
        pm.write_int(address_list["TALK_ID"], 0)
        pm.write_bytes(address_list["NPC_ENEMY_TYPE"], b"\x00", 1)
        # WRITE CHR INFO #
        spawned_enemy = address_list["SPAWN_ADDR"].to_bytes(8, byteorder="little")
        worldchrman = address_list["WORLDCHRMAN"].to_bytes(8, byteorder="little")
        assembly_code = (
            b"\x48\xA1" + worldchrman + b"\x48\x8B\x80\x40\xE6\x01\x00"
            b"\xC6\x40\x44\x01"
            b"\x8B\x15\x30\x00\x00\x00"
            b"\x6B\xD2\x10"
            b"\x48\xBB" + spawned_enemy + b"\x48\x01\xD3"
            b"\x8A\x80\x78\x01\x00\x00"
            b"\x88\x43\x0B"
            b"\xFF\x05\x11\x00\x00\x00"
            b"\xC3"
        )
        l = allocate_mem
        # print(format(l,'X'))
        pm.write_bytes(l, assembly_code, len(assembly_code))
        # print(pm.read_int(l+0x4B))
