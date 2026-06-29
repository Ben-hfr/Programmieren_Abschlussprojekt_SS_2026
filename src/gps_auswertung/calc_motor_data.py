import numpy as np

class Calc_Motor_Data():
    """calculates the torque at the driven wheel and the resulting motor
        current, based on the required force from Calc_Force_Data and the
        motor's characteristic data (wheel radius, motor constant)
 
        Vereinfachtes Modell: Radnabenmotor ohne Getriebe (von Angabe) -> Motordrehmoment
        entspricht 1:1 dem Drehmoment am Rad. Nur ein Rad wird angetrieben,
        daher wirkt die komplette Kraft F an diesem einen Rad.

        evtl Erweiterung = Motor mit verschiedenen Getrieben
 
        possible functions are:"""
    
    def __init__(self, force_calc , d_wheel: float, k_m: float): #k_m = motorconstant
        """
        takes:
            force_calc: an already created instance of Calc_Force_Data
            d_wheel: Wheeldiameter [zoll]
            k_m: Motorconstant [Nm/A]
        """
        self.force_calc = force_calc
        #umrechnung von Zoll in m (1 Zoll = 2.54cm) und durchmesser in Radius
        self.r_wheel = (d_wheel * 0.0254) / 2 
        self.k_m = k_m
 
        self.torque = 0
        self.current = 0

    def get_torque(self) -> np.ndarray:
        """
        takes:
            required force from Calc_Force_Data, r_wheel
        does:
            calculates the torque at the driven wheel: T = F * r_wheel
            (nur ein Rad angetrieben -> die komplette Kraft F wirkt hier)
        returns:
            Torque in Nm for every timedelta
        """

        F = self.force_calc.get_required_force()

        self.torque = F * self.r_wheel

        return self.torque
    
    def get_motor_current(self) -> np.ndarray:
        """
        takes:
            torque from get_torque(), K_m
        does:
            calculates the motor current via T = K_m * I_mot -> I_mot = T / K_m
        returns:
            Motorcurrent in A for every Timedelta
        """

        self.get_torque()

        self.current = self.torque / self.k_m

        return self.current