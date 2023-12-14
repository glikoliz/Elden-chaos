import pymem
import threading
import random
from getaddress import get_final_list
import functions as call
def p(v): #for debugging
    if isinstance(v, list):
        print([format(i) for i in v])
    elif isinstance(v, dict):
        for key, value in v.items():
            print(f"{format(value,'X')}  {key}")
    else:
        print(format(v, 'X'))
def isdead(): #addresses changes after you die
    if(pm.read_int(final_list["CUTSCENE_ON"])!=0):
        return True
    return False
def goalive():
    global final_list
    while pm.read_int(final_list['CUTSCENE_ON'])!=0: #wait until addresses change
        pass
    final_list=get_final_list(pm)
pm=pymem.Pymem('eldenring.exe')
final_list=get_final_list(pm)
p(final_list)
call.GODRICK_TIME(pm, final_list)
# call.WARP(pm, final_list)
# call.MANA_LEAK(pm, final_list)

