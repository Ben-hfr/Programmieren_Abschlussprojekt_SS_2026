import numpy as np
from src.gps_auswertung.calc_gps_data import Calc_GPS_Data

class Calc_Force_Data():
    """calculates the force and the power needed to drive the e-bike, based on kinematic data (speed, acceleration, gradient)
    from an existing Calc_GPS_Data instance and a few physical parameters of bike + rider

    possible functions are:"""

    def __init__(self, gps_calc: Calc_GPS_Data, mass: float, cw: float, area: float,
                 rho: float = 1.225, c_roll: float = 0.0, g: float = 9.81):
        """
        takes:
            gps_calc: an already created instance of Calc_GPS_Data
            mass: total mass of e-bike + rider [kg]
            cw: drag coefficient of bike + rider [-]
            area: frontal area [m^2]
            rho: air density [kg/m^3] (default: 1.225 -> 15°C, sea level)
            c_roll: rolling resistance coefficient [-] (default: 0, optional)
            g: gravitational acceleration [m/s^2] (default = 9,81)
        """
        self.gps_calc = gps_calc 
        self.mass = mass
        self.cw = cw
        self.area = area
        self.rho = rho
        self.c_roll = c_roll
        self.g = g

        self.F_drag = 0
        self.F_gravity = 0
        self.F_roll = 0
        self.F_acc = 0
        self.F_required = 0
        self.power = 0

    def get_drag_force(self) -> np.ndarray:
        """
        takes:
            speed from Calc_GPS_Data
        does:
            calculates the air drag force F_D = 0.5 * rho * cw * A * v^2
        returns:
            drag force in N for each time delta
        """

        speed_ms = self.gps_calc.get_speed() / 3.6

        self.F_drag = (self.rho * self.cw * self.area * speed_ms**2) / 2

        return self.F_drag



        