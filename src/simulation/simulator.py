#package imports
import sys
import numpy as np
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent

# Den Pfad zum sys.path hinzufügen, falls er noch nicht drin ist
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#class imports 
from src.simulation.LiPo_battery import LiPoBattery
from src.simulation.NMC_battery import NMCBattery

class Simulator():

    def __init__ (self, battery_type, current_profile: np.ndarray):
        self.battery = battery_type
        self.C = current_profile

        self.d_time = 1 
        self.voltage_profile = np.array([])
        self.Soc_profile = np.array([])

    def simulate(self) -> None: 
       
        self.Soc_profile =  self.battery.apply_current(self.C, self.d_time)

        self.voltage_profile = self.battery.get_voltage(self.C)
        


    def get_result(self) -> tuple[np.ndarray, np.ndarray]:
        self.simulate()
        return (self.voltage_profile, self.Soc_profile)


if __name__ == "__main__":

    from src.simulation.LiPo_battery import LiPoBattery

    Lipo_battery = LiPoBattery()
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    
    Lipo_battery.apply_current(100, 300)
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    
