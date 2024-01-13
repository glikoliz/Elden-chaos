import pymem
import json
import re

def get_address_with_offsets(pm, addr, offsets):
    for i in offsets:
        if(i!=offsets[-1]):
            addr=pm.read_longlong(addr+i)
    return addr+offsets[-1]

def get_worldchrman(pm, module_data):
    address = pm.base_address + re.search(rb'\x48\x8B\x05....\x48\x85\xC0\x74\x0F\x48\x39\x88', module_data).start()
    return address+pm.read_int(address+3)+7

def get_event_flag_man(pm, module_data):
    address=pm.base_address + re.search(rb'\x48\x8B\x3D....\x48\x85\xFF..\x32\xC0\xE9', module_data).start()
    return address+pm.read_int(address+3)+7

def get_cs_lua_event(pm, module_data):
    address=pm.base_address + re.search(rb'\x48\x8B\x05....\x48\x85\xC0\x74.\x41\xBE\x01\x00\x00\x00\x44\x89\x75', module_data).start()
    return pm.read_longlong(address+pm.read_int(address+3)+7)

def get_lua_warp(pm, module_data):
    address=pm.base_address + re.search(rb'\xC3......\x57\x48\x83\xEC.\x48\x8B\xFA\x44', module_data).start()
    return address+2

def get_fast_travel(pm, module_data):
    address = pm.base_address+re.search(rb'\x48\x8B\x0D....\x48...\x44\x0F\xB6\x61.\xE8....\x48\x63\x87....\x48...\x48\x85\xC0', module_data).start()
    # print(address)
    return pm.read_longlong(address+pm.read_int(address+3)+7)+0xA0

def get_chr_dbg_flags(pm, module_data):
    address = pm.base_address+re.search(rb'\x80\x3D....\x00\x0F\x85....\x32\xC0\x48', module_data).start()
    return address+pm.read_int(address+2)+7
def get_spawn_addr(pm, worldchrman):
    addr=worldchrman
    addr=pm.read_longlong(addr)+0x1E1C0
    addr=pm.read_longlong(addr)+0x18
    return pm.read_longlong(addr)
def get_gamedataman(pm, module_data):
    address = pm.base_address+re.search(rb'\x48\x8B\x05....\x48\x85\xC0\x74\x05\x48\x8B\x40\x58\xC3\xC3', module_data).start()
    return address+pm.read_int(address+3)+7
def get_cs_flipper(pm, module_data):
    address = pm.base_address+re.search(rb'\x48\x8B\x0D....\x80\xBB\xD7\x00\x00\x00\x00\x0F\x84\xCE\x00\x00\x00\x48\x85\xC9\x75\x2E', module_data).start()
    return address+pm.read_int(address+3)+7
def get_chr_dbg(pm, module_data):
    address=pm.base_address+re.search(rb'\x48\x8B\x05....\x41\x83\xFF\x02..\x48\x85\xC0', module_data).start()
    return address+pm.read_int(address+3)+7
def p(v):
    if isinstance(v, list):
        print([format(i) for i in v])
    elif isinstance(v, dict):
        for key, value in v.items():
            print(f"{key}  {format(value,'X')}")
    else:
        print(format(v, 'X'))
        
def get_address_list(pm):
    ##### INIT #####
    process_module = pymem.process.module_from_name(pm.process_handle, 'eldenring.exe')
    module_data = pm.read_bytes(pm.base_address, process_module.SizeOfImage)
    variables = {"worldchrman": pm.read_longlong(get_worldchrman(pm, module_data)),
                 "eventflagman":pm.read_longlong( get_event_flag_man(pm, module_data)),
                 'gamedataman': pm.read_longlong(get_gamedataman(pm, module_data)),
                 'csflipper' : pm.read_longlong(get_cs_flipper(pm, module_data))}
    # p(variables)
    address_list={}
    ##### INIT #####
    
    with open('addresses.json', 'r') as file:
        json_data = json.load(file)
    for obj in json_data:
        name=obj["name"]
        addr=obj["addr"]
        offsets=obj["offsets"]
        try:
            addr=int(obj["addr"],16)
        except:
            addr=variables.get(addr, 0)
        list_offsets=[int(element, 16) for element in offsets.split()]
        address_list[name]=get_address_with_offsets(pm, addr, list_offsets)
    # final_list["WARP_FUNC"], final_list["WARP_LOCATION"]=alloc_warp(pm, module_data)
    address_list["FAST_TRAVEL"]=get_fast_travel(pm, module_data)
    address_list["WORLDCHRMAN"]=get_worldchrman(pm, module_data)
    address_list["SPAWN_ADDR"]=get_spawn_addr(pm, address_list['WORLDCHRMAN'])
    address_list["LUA_WARP"]=get_lua_warp(pm, module_data)
    address_list["CS_LUA_EVENT"]=get_cs_lua_event(pm, module_data)
    address_list["CHR_DBG_FLAGS"]=get_chr_dbg_flags(pm, module_data)
    address_list["CHR_DBG"]=pm.read_longlong(get_chr_dbg(pm, module_data))
    
    
    return address_list

if __name__=='__main__':
    pm = pymem.Pymem('eldenring.exe')
    p(get_address_list(pm))