import pymem
from time import sleep
from random import randint
from linecache import getline
class Funcs:
    def disable_fast_travel(pm, final_list):
        pm.write_bytes(pm.base_address+0x61F232, b'\xBB\x01\x00\x00\x00\x89\x9E\xA0\x00\x00\x00', 11)
    def enable_fast_travel(pm, final_list): #todo
        pm.write_bytes(pm.base_address+0x61F232, b'\xBB\x00\x00\x00\x00\x89\x9E\xA0\x00\x00\x00', 11)
    def warp_to(pm, final_list, grace):
        pm.write_int(final_list["WARP_LOCATION"], grace)
        pm.start_thread(final_list["WARP_FUNC"])
        
    def wait(pm, final_list):
        while(pm.read_int(final_list["CUTSCENE_ON"])!=0):
            sleep(0.1)
    def respawn_boss(pm, boss_addr):
        pm.write_uchar(boss_addr, 0)
    def spawn_enemy(pm, final_list, id): #TODO:chr_count may be broken
        # WRITE CURRENT POS #
        pm.write_bytes(final_list["SPAWN_NPC_X"], pm.read_bytes(final_list['CURRENT_POS'], 12), 12)
        # WRITE CURRENT POS #
        
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
def print_name(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
@print_name("One Hit KO")
def OHKO(pm, final_list):
    basehp=pm.read_int(final_list['MAX_HP'])
    pm.write_int(final_list['MAX_HP'], 1)
    sleep(10)
    pm.write_int(final_list['MAX_HP'], basehp)
@print_name("Mana leak")
def MANA_LEAK(pm, final_list):
    fp=pm.read_int(final_list['FP'])
    while(fp>=3):
        fp=pm.read_int(final_list['FP'])-3
        pm.write_int(final_list['FP'], fp)
        sleep(0.5)
@print_name("Teleport to random grace")
def WARP(pm, final_list):
    random_number=int(getline("graces.txt", randint(0, 305)).strip())
    Funcs.warp_to(pm, final_list, random_number)
@print_name("Rick, Soldier of God")
def GODRICK_TIME(pm, final_list):
    Funcs.respawn_boss(pm, final_list["GODRICK"])
    Funcs.disable_fast_travel(pm, final_list)
    Funcs.warp_to(pm, final_list, 18002950)
    while pm.read_uchar(final_list["GODRICK"])==0: #wait until godrick dies
        sleep(0.5)
        pass
    Funcs.enable_fast_travel(pm, final_list)
def spawn_melania(pm, final_list):
    Funcs.spawn_enemy(pm, final_list, 2120)