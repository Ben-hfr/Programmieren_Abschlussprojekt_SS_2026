#package imports
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d

#class imports 
project_root = Path(__file__).resolve().parent
from src.simulation.battery_base import Battery

class NMCBattery (Battery):

    def __init__(self,
            number_of_cells: int,                
            internal_resistance_mOhm: float = 7,
            capacity_mAh: float = 5000,                  
            initial_soc: float = 100.0,
                ):
        super().__init__(
            capacity_mAh = capacity_mAh,
            number_of_cells = number_of_cells,
            internal_resistance_mOhm = internal_resistance_mOhm,
            initial_soc = initial_soc
        )
        voltage_profile = np.array([
                32.00, 32.61, 33.17, 33.85, 34.24, 34.66, 35.39, 
                35.65, 36.65, 37.64, 38.91, 40.14, 41.08, 42.00])
        soc_measurement_points = np.array([
                0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 
                0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00])
        self.function = interp1d(soc_measurement_points, voltage_profile, kind = "cubic")  


    def get_voltage(self, current: float = 0.0) -> float:
        
        return self.function(self.soc) - self.R_int * current