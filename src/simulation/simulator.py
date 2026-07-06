#package imports
import sys
import numpy as np
from pathlib import Path
import logging

#logging initialisieren 
logger = logging.getLogger(__name__)

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

        self.empty_error_triggered = False
        self.empty_at_index = None
        self.dissipated_energy_j = 0.0

        #Info Log 
        logger.info(f"Simulator initialized for {self.battery.__class__.__name__}")

    def simulate(self) -> None:         
        theoretical_soc =  self.battery.apply_current(self.C, self.d_time)
        self.Soc_profile =  np.copy(theoretical_soc)

        #find every index where soc is under 0 and give first one  
        empty_indices = np.where(theoretical_soc < 0.0)[0]
        
        if empty_indices.size > 0:
            #sobald einmal leer. dann alle nachfolgenden werte auf 0 und index speichern 
            self.empty_error_triggered = True
            self.empty_at_index = empty_indices[0]

            logger.warning(
                f"Battery went empty during simulation! "
                f"First empty state at index {self.empty_at_index}."
            )

            self.Soc_profile[theoretical_soc < 0] = 0.0
        
        overflow_indices = np.where(theoretical_soc > 1.0)[0]

        if overflow_indices.size > 0:
            
            # soc overflow per time delta
            soc_diff = np.diff(theoretical_soc, prepend=self.battery.initial_soc)

            #only use the current when battery was already full
            overshoot_soc_steps = soc_diff[theoretical_soc > 1.0]

            #voltage when battery is full
            v_full = self.battery.get_voltage(soc = 1)
            
            # Calculate energie (E = C * U) with C = I * t 
            self.dissipated_energy_j = np.sum(overshoot_soc_steps) * self.battery.capacity * v_full

            logger.info(
                f"Battery overflow detected. "
                f"Dissipated energy: {self.dissipated_energy_j:.2f} Joules."
            )

            # all values over one get cliped to one        
            self.Soc_profile[theoretical_soc > 1.0] = 1.0
        
        self.battery.soc_profile = self.Soc_profile
        self.voltage_profile = self.battery.get_voltage(self.C)
        

    def get_result(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Runs the Simulation with the given Battery Type and current profile.
        
        Returns: 
            Tuple(Voltage Profile, SoC Profile)
        """
        self.simulate()
        return (self.voltage_profile, self.Soc_profile)

    def get_error(self) -> tuple[bool, int]:
        return (self.empty_error_triggered, self.empty_at_index)

if __name__ == "__main__":

    from src.simulation.LiPo_battery import LiPoBattery
    from src.simulation.NMC_battery import NMCBattery

    Lipo_battery = LiPoBattery()
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    
    Lipo_battery.apply_current(100, 300)
    print(f"Battery Full = {Lipo_battery.is_full()}")
    print(Lipo_battery)
    

    NMC_battery = NMCBattery()
    print(f"Battery Full = {NMC_battery.is_full()}")
    print(NMC_battery)
    
    NMC_battery.apply_current(100, 300)
    print(f"Battery Full = {NMC_battery.is_full()}")
    print(NMC_battery)
    NMC_battery_simulator = Simulator(NMC_battery, -100)
    NMC_battery_simulator.simulate()
    print(f"Energy dissipated of the resistor where {NMC_battery_simulator.dissipated_energy_j} Joule")