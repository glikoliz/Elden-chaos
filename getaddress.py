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
    variables = {"worldchrman": pm.read_longlong(get_worldchrman(pm, module_data)),
                 "eventflagman": pm.read_longlong(get_event_flag_man(pm, module_data))}
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
    return final_list
if __name__=='__main__':
    pm = pymem.Pymem('eldenring.exe')
    p(get_final_list())