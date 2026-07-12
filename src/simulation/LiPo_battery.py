#package imports
import numpy as np
from pathlib import Path
from scipy.interpolate import interp1d

#class imports 
project_root = Path(__file__).resolve().parent
from src.simulation.battery_base import Battery

class LiPoBattery (Battery):

    def __init__(self,
            number_of_rows: int = 10,                
            internal_resistance_mOhm: float = 8,
            capacity_mAh: float = 5000,                  
            initial_soc: float = 100.0,
                ):
        super().__init__(
            capacity_mAh=capacity_mAh,
            number_of_rows=number_of_rows,
            internal_resistance_mOhm=internal_resistance_mOhm,
            initial_soc=initial_soc
        )
        voltage_profile = np.array([
                32.00, 35.87, 36.85, 37.56, 37.87, 38.28, 38.81, 
                39.05, 39.55, 40.27, 40.70, 41.16, 41.65, 42.00])
        soc_measurement_points = np.array([
                0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 
                0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00])
        self.function = interp1d(soc_measurement_points, voltage_profile, kind = "cubic")  

        self.rows_in_parralel = number_of_rows
 

    def get_voltage(self, current: float = 0.0, soc: np.ndarray = None) -> np.ndarray:
        #check if soc is given, if not use self.soc_profile, if, then use value
        actual_soc = self.soc_profile if soc is None else soc
        
        #return value of function minus voltage over internal resistance 
        return self.function(actual_soc) - self.R_int * current
    

