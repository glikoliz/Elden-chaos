import pymem
from time import sleep
def OHKO(pm, addr):
    basehp=pm.read_int(addr)
    pm.write_int(addr, 1)
    sleep(10)
    pm.write_int(addr, basehp)
    return "OHKO"
# if __name__=='__main__':
    # pm=pymem.Pymem('eldenring.exe')