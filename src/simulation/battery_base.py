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
            number_of_cells: The total number of cellrows (one row = 10 cells) in parallel  
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
        self.R_int = (internal_resistance_mOhm * 10**(-3) * 10) / number_of_cells #converts to Ohm and multiplies by ten, because ten in a row. devides by number of cell rows in parallel 
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
        # soc delta for a specific duration
        soc_d = - (current * duration) / self.capacity 
        
        # cumulitve sum for the soc deltas  
        cumulativ_deltas = np.cumsum(soc_d) 

        #adds the initial soc as the first value
        soc_ges = self.initial_soc + cumulativ_deltas

        #temporary help so that the values dont go above 1 and below 0
        #soc_ges = np.clip(soc_ges, 0.0, 1.0)

        #put soc value as the last value of array 
        self.soc = soc_ges[-1]

        #put the total soc values (array) as soc profile 
        self.soc_profile = soc_ges

        return soc_ges 


    def is_empty(self) -> bool:
        """
        returns:
            True if battery is empty (SoC = 0)
            False if battery has charge left (SoC != 0)
        """
        if self.soc_profile.size == 0:
            return np.isclose(self.initial_soc, 0.0)
        else:
            return np.isclose(self.soc, 0.0)
        

    def is_full(self) -> bool:
        """
        returns:
            True if battery is full (SoC = 100%)
            False if battery SoC is under 100%(SoC != 100%)
        """
        if self.soc_profile.size == 0:
            return np.isclose(self.initial_soc, 1.0)    
        else:
            return np.isclose(self.soc, 1.0)
    
    def __str__(self):
        #if soc profile is empty because just intialized the voltage is calculated with initial soc, otherwise the last value of the voltage array
        if self.soc_profile.size == 0:
            return f"BatteryPack(SoC={self.initial_soc * 100:.1f}%, V={self.get_voltage(soc = self.initial_soc):.2f} V)"
        else:
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