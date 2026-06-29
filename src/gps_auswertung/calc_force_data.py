import numpy as np

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
            speed from Calc_GPS_Data, rho, cw, area
        does:
            calculates the air drag force F_D = 0.5 * rho * cw * A * v^2
        returns:
            drag force in N for each time delta
        """

        #get speed as m/s
        speed_ms = self.gps_calc.get_speed() / 3.6

        #calculate drag force
        self.F_drag = (self.rho * self.cw * self.area * speed_ms**2) / 2

        return self.F_drag
    
    def get_gravity_force(self) -> np.ndarray:
           """
        takes:
            gradient from Calc_GPS_Data, g, mass
        does:
            calculates the force component along the slope (Hangabtriebskraft)
            F_g = m * g * sin(phi)
        returns:
            gravity force in N for each time delta
        """
           
           #Get gradient as rad
           phi_rad = np.deg2rad(self.gps_calc.get_gradient_deg())

           #Calculate gravity-force
           self.F_gravity = self.mass * self.g * np.sin(phi_rad)

           return self.F_gravity
    
    def get_rolling_resistance(self) -> np.ndarray:
        """
        takes:
            gradient from Calc_GPS_Data, c_roll, mass, g
        does:
            calculates the rolling resistance F_r = c_roll * m * g * cos(phi)
            (optional, default c_roll = 0)
        returns:
            rolling resistance in N for each time delta
        """
        phi_deg = self.gps_calc.get_gradient_deg()
        phi_rad = np.deg2rad(phi_deg)
 
        self.F_roll = self.c_roll * self.mass * self.g * np.cos(phi_rad)
 
        return self.F_roll
    
    def get_acceleration_force(self) -> np.ndarray:
        """
        takes:
            acceleration from Calc_GPS_Data, mass, acceleration
        does:
            calculates the force needed to accelerate: F_a = m * a
        returns:
            acceleration force in N for each time delta
        """
        acc = self.gps_calc.get_acceleration()
 
        self.F_acc = self.mass * acc
 
        return self.F_acc
    
    def get_required_force(self) -> np.ndarray:
        """
        takes:
            all single forces calculated in this class
        does:
            sums up all forces along the direction of travel to get the
            force the e-bike (motor + pedalling) needs to provide,
            based on Newton's second law:
            F_required = F_acc + F_drag + F_gravity + F_roll
        returns:
            required driving force in N for each time delta
        """
        F_acc = self.get_acceleration_force()
        F_drag = self.get_drag_force()
        F_gravity = self.get_gravity_force()
        F_roll = self.get_rolling_resistance()
 
        self.F_required = F_acc + F_drag + F_gravity + F_roll
 
        return self.F_required

    
    def get_power(self) -> np.ndarray:
        """
        takes:
            required force and speed
        does:
            calculates the power needed: P = F * v
        returns:
            power in Watt for each time delta
        """
        F = self.get_required_force()
        speed_ms = self.gps_calc.get_speed() / 3.6
 
        self.power = F * speed_ms
 
        return self.power
    


        