#package imports
import numpy as np

#class imports 
from LiPo_battery import LiPoBattery

class simulator():

    def __init__ (self):
        pass 

    def simulate():
        pass 


if __name__ == "__main__":

    Lipo_battery = LiPoBattery(10, 0.008)
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    
    Lipo_battery.apply_current(100, 300)
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    
