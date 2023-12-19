import pymem
from time import sleep
from random import randint, choice
from linecache import getline
class Funcs:
    def disable_fast_travel(pm, final_list):
        pm.write_bytes(pm.base_address+0x61F232, b'\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00', 11)
    def enable_fast_travel(pm, final_list): #TODO:can be better
        pm.write_bytes(pm.base_address+0x61F232, b'\xBB\x00\x00\x00\x00\x89\x9E\xA0\x00\x00\x00', 11)
    def warp_to(pm, final_list, grace):
        print("ALLOCATING WARP_FUNC")
        warp_func=pm.allocate(100)
        cs_lua_event=final_list['CS_LUA_EVENT'].to_bytes(8, byteorder='little')
        lua_warp=final_list['LUA_WARP'].to_bytes(8, byteorder='little')
        bytecode = (
        b'\x48\x83\xEC\x48'
        b'\x48\xB8' + cs_lua_event +
        b'\x48\x8B\x48\x18'
        b'\x48\x8B\x50\x08' 
        b'\x8B\x05\x1C\x00\x00\x00'
        b'\x44\x8D\x80\x18\xFC\xFF\xFF\xFF\x15\x02\x00\x00\x00'
        b'\xEB\x08' + lua_warp +
        b'\x48\x83\xC4\x48'
        b'\xC3' 
        )
        warp_loc=warp_func+len(bytecode)
        # addr=pm.allocate(len(bytecode))
        pm.write_bytes(warp_func, bytecode, len(bytecode))
        pm.write_int(warp_loc, grace)
        print("DO WARP")
        pm.start_thread(warp_func)
        print("FREE WARP")
        
        pm.free(warp_func)
        
    def wait(pm, final_list):
        while(pm.read_int(final_list["CUTSCENE_ON"])!=0):
            sleep(0.1)
    def respawn_boss(pm, boss_addr):
        pm.write_uchar(boss_addr, 0)
    def spawn_enemy(pm, final_list, id): #TODO:chr_count may be broken
        pm.write_bytes(final_list["SPAWN_NPC_X"], pm.read_bytes(final_list['CURRENT_POS'], 12), 12)# WRITE CURRENT POS
        
        # WRITE CHR INFO #
        chr_id=("c"+str(id)).encode("utf-16le")
        pm.write_bytes(final_list["CHR_ID"], chr_id, len(chr_id))
        pm.write_int(final_list["NPC_PARAM_ID"], id*10000)
        pm.write_int(final_list["NPC_THINK_PARAM_ID"], id*10000)
        pm.write_int(final_list["EVENT_ENTITY_ID"], 0)
        pm.write_int(final_list["TALK_ID"], 0)
        pm.write_bytes(final_list['NPC_ENEMY_TYPE'], b'\x00', 1)
        # WRITE CHR INFO #
        spawned_enemy=final_list["SPAWN_ADDR"].to_bytes(8, byteorder='little')
        worldchrman=final_list['WORLDCHRMAN'].to_bytes(8, byteorder='little')
        assembly_code = (
        b'\x48\xA1'+worldchrman+
        b'\x48\x8B\x80\x40\xE6\x01\x00'
        b'\xC6\x40\x44\x01'
        b'\x8B\x15\x30\x00\x00\x00'
        b'\x6B\xD2\x10'
        b'\x48\xBB'+spawned_enemy+
        b'\x48\x01\xD3'
        b'\x8A\x80\x78\x01\x00\x00'
        b'\x88\x43\x0B'
        b'\xFF\x05\x11\x00\x00\x00'
        b'\xC3'
        )
        l=pm.allocate(100)
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
        (GODRICK_TIME, "Rick, Soldier of God"),
        (SPAWN_MALENIA, "Spawn Melania")
    ]
    random_function, function_name = choice(functions)
    return random_function, function_name
def OHKO(pm, final_list):
    basehp=pm.read_int(final_list['MAX_HP'])
    pm.write_int(final_list['MAX_HP'], 1)
    sleep(10)
    pm.write_int(final_list['MAX_HP'], basehp)
def MANA_LEAK(pm, final_list):
    fp=pm.read_int(final_list['FP'])
    while(fp>=3):
        fp=pm.read_int(final_list['FP'])-3
        pm.write_int(final_list['FP'], fp)
        sleep(0.5)
def WARP_TO_RANDOM_GRACE(pm, final_list):
    random_number=int(getline("graces.txt", randint(0, 305)).strip())
    Funcs.warp_to(pm, final_list, random_number)
def GODRICK_TIME(pm, final_list):
    Funcs.respawn_boss(pm, final_list["GODRICK"])
    Funcs.disable_fast_travel(pm, final_list)
    Funcs.warp_to(pm, final_list, 18002950)
    while pm.read_uchar(final_list["GODRICK"])==0: #wait until godrick dies
        sleep(0.5)
        pass
    Funcs.enable_fast_travel(pm, final_list)
def SPAWN_MALENIA(pm, final_list):
    Funcs.spawn_enemy(pm, final_list, 2120)