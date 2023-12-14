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
    return pm.read_longlong(address+pm.read_int(address+3)+7)

def get_event_flag_man(pm, module_data):
    address=pm.base_address + re.search(rb'\x48\x8B\x3D....\x48\x85\xFF..\x32\xC0\xE9', module_data).start()
    return pm.read_longlong(address+pm.read_int(address+3)+7)

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


def alloc_warp(pm, module_data):
    cs_lua_event=get_cs_lua_event(pm, module_data).to_bytes(8, byteorder='little')
    lua_warp=get_lua_warp(pm, module_data).to_bytes(8, byteorder='little')
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
    addr=pm.allocate(len(bytecode))
    pm.write_bytes(addr, bytecode, len(bytecode))
    return addr, addr+len(bytecode) #return address for warp func and warp location

def p(v):
    if isinstance(v, list):
        print([format(i) for i in v])
    elif isinstance(v, dict):
        for key, value in v.items():
            print(f"{key}  {format(value,'X')}")
    else:
        print(format(v, 'X'))
        
def get_final_list(pm):
    ##### INIT #####
    process_module = pymem.process.module_from_name(pm.process_handle, 'eldenring.exe')
    module_data = pm.read_bytes(pm.base_address, process_module.SizeOfImage)
    variables = {"worldchrman": get_worldchrman(pm, module_data),
                 "eventflagman": get_event_flag_man(pm, module_data)}
    final_list={}
    ##### INIT #####
    
    with open('ok.json', 'r') as file:
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
        final_list[name]=get_address_with_offsets(pm, addr, list_offsets)
    final_list["WARP_FUNC"], final_list["WARP_LOCATION"]=alloc_warp(pm, module_data)
    final_list["FAST_TRAVEL"]=get_fast_travel(pm, module_data)
    return final_list

if __name__=='__main__':
    pm = pymem.Pymem('eldenring.exe')
    p(get_final_list(pm))