#package imports
from abc import ABC, abstractmethod
import numpy as np

class Battery(ABC):

    def __init__(
            self,
            capacity_mAh: float,
            number_of_cells: int,
            internal_resistance_mOhm: float,
            initial_soc: float = 100.0,
            ):
        """
        takes:
            capacity_mAh: The nominal capacity for one Cell in mAh
            number_of_cells: The total number of cellrows parallel  
            internal_resistance_Ohm: the resistance of one Cell in mOhm
            initial_soc: the ammount of battery charge in percent (Standart = 100) 
        
        Possible Functions are:
            - apply_current 
            - is_empty
            - is_full 
            - get_voltage
        """
        
        if capacity_mAh <= 0:
            raise ValueError("capacity must be greater than 0!")
        
        self.capacity = capacity_mAh * 3.6 * number_of_cells  #converts mAh As (Si)
        self.R_int = internal_resistance_mOhm * 10**(-3) 
        #self.soc = max(0.0, min((initial_soc / 100), 1.0))
        #self.soc = np.clip((initial_soc / 100), 0.0, 1.0)
        self.initial_soc = (initial_soc / 100)
        self.soc = 0
        self.soc_profile = np.array([])
        self.empty = False
        self.full = False
    
    def apply_current(self, current: np.ndarray, duration: float) -> np.ndarray:
        """
        takes:
            current: current in drawn [Amps]
            duration: time of each current draw [seconds]
        does:
            Applys a current for a spcific duration in seconds and update the SoC
        retuns:
            cumulative array with soc 
        """
        
        soc_d = - (current * duration) / self.capacity # soc delta for a specific duration

        cumulativ_deltas = np.cumsum(soc_d)

        soc_ges = self.initial_soc + cumulativ_deltas

        soc_ges = np.clip(soc_ges, 0.0, 1.0)

        self.soc = soc_ges[-1]

        self.soc_profile = soc_ges

        return soc_ges 


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
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.get_voltage()[-1]:.2f} V)"

    @abstractmethod
    def get_voltage(self, current: float) -> float:
        """
        takes: 
            current: Current drawn under load [A] (standart = 0)
        does:
            calculates the output voltage for SoC at that moment
        returns:
            outpout voltage 
        """
        pass