from abc import ABC, abstractmethod
import numpy as np

class Battery(ABC):

    def __init__(
            self,
            capacity_mAh: float,
            number_of_cells: int,
            internal_resistance_Ohm: float,
            initial_soc: float = 100.0,
            ):
        """
        takes:
            capacity_mAh: The nominal capacity for one Cell in mAh
            number_of_cells: The total number of cells in a row 
            internal_resistance_Ohm: the resistance of one Cell in Ohm
            initial_soc: the ammount of battery charge in percent (Standart = 100) 

        """
        
        if capacity_mAh <= 0:
            raise ValueError("capacity must be greater than 0!")
        
        self.capacity = number_of_cells * capacity_mAh * 3.6  #converts mAh As (Si)
        self.R_int = internal_resistance_Ohm
        self.soc = max(0.0, min((initial_soc / 100), 1.0))
        #self.Vmin = voltage_profile[0]
        #self.Vmax = voltage_profile[-1]

        self.empty = False
        self.full = False
    
    def apply_current(self, current: float, duration: float) -> None:
        """
        Apply a current for a spcific duration in seconds and update the SoC
        """
        soc_d = - (current * duration) / self.capacity # soc delta for a specific duration
        self.soc = max(0.0, min(self.soc + soc_d, 1.0))


    def is_empty(self) -> bool:
        """
        returns:
            True if battery is empty (SoC = 0)
            False if battery has charge left (SoC != 0)
        """
        return np.isclose(self.soc, 0.0)
        

    def is_full(self) -> bool:
        """
        returns:
            True if battery is full (SoC = 100%)
            False if battery SoC is under 100%(SoC != 100%)
        """
        return np.isclose(self.soc, 1.0)
    
    def __str__(self):
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.get_voltage():.2f} V)"

    @abstractmethod
    def get_voltage(self) -> float:
        pass