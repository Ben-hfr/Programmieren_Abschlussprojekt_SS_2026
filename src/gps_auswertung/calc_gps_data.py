import numpy as np
from scipy.signal import savgol_filter 

class Calc_GPS_Data():
    """calculates different values for a given np.array from a gps-csv-file
    
        possble functions are:"""
    def __init__(self, gps_array: np.ndarray, window_size: int, polyorder: int):
        """
        takes:
            window_size: size of window for Savitzky-Golay Filter
            polyorder: The order of polynomial for Savitzky-Golay Filter. This must be less than window_size!
        """
        self.window_size = window_size
        self.polyorder = polyorder
        self.gps_array = gps_array

        
        self.dist = 0
        self.dist_2d = None
        self.speed_ms = 0
        self.acc = 0
        self.altitude = 0
        self.total_time = 0
        self.rho = 0

        self.dtime_sec = 1
        #get time
        #time = self.gps_array[:,3]
        #calculate time delta 
        #dtime = np.diff(time)
        #convert time deltas to seconds
        #self.dtime_sec = dtime.astype('timedelta64[ms]').astype(float) / 1000.0


    def get_distance(self) -> float:
        """
        takes:
            given Numpy array of GPS-Data
        does:
            this method calculates the distance for each time delta in the given GPS Data and saves it as self.dist.
            The Data is filtered usinging the Savitzky-Golay Filter and the values given in the Constructor 
        """

        #define Erd Raduis [m]
        R = 6371000.0

        #Lat/Long und höhe in einzelne Arrays speichern und Längen/Breiten -grad in Radiant umrechnen 
        #astype(float) is needed because array is type obejct and not float
        lat = np.deg2rad(self.gps_array[:,0].astype(float))
        lon = np.deg2rad(self.gps_array[:,1].astype(float))
        alt = self.gps_array[:,2].astype(float)

        #Calculates the delta i+1 and i with np.diff
        dlat = np.diff(lat)
        dlon = np.diff(lon)
        dalt = np.diff(alt)

        #define start and end 
        lat_start = lat[:-1]
        lat_end = lat[1:]

        #Haversine formular
        help_d = np.sqrt(np.sin(dlat/2)**2 + np.cos(lat_start) * np.cos(lat_end) * np.sin(dlon / 2)**2)
        distance_2d = 2 * R * np.arcsin(help_d)
        self.dist_2d = distance_2d

        #3D Distance with altitude 
        self.dist = np.sqrt((distance_2d**2) + (dalt**2))

        return self.dist


    def get_speed(self) -> np.ndarray:
        """
        takes:
            given Numpy array
        does:
            this method calculates the velocity for each time delta in the given GPS Data
        returns:
            calculates the velocity in kmh 
        """
        
        #get distance array with method to use later on 
        self.get_distance()

        #calculate speed
        #self.dtime_sec = np.where(self.dtime_sec == 0, 1e-5, self.dtime_sec)
        speed_raw = self.dist / self.dtime_sec

        #filter 
        self.speed_ms = savgol_filter(speed_raw, self.window_size, self.polyorder, mode="nearest")

        #speed cannot be negative
        self.speed_ms = np.where(self.speed_ms < 0, 0.0, self.speed_ms)

        return self.speed_ms * 3.6
    
    def get_acceleration(self) -> np.ndarray:
        """
        takes:
            speed numpy array
        does:
            this method calculates the acceleration for each time delta in the given GPS Data
        returns:
            calculates the acceleration in m/s^2
        """

        #get speed
        self.get_speed()
        dspeed = np.diff(self.speed_ms)
        dspeed = np.concatenate(([0], dspeed))
        acc_raw = dspeed / self.dtime_sec

        self.acc = savgol_filter(acc_raw, self.window_size, self.polyorder,
                                 mode="nearest")
    
        return self.acc

    def get_altitude(self) -> np.ndarray:
        """ 
        takes:
            given Numpy array 
        does:
            this method extracts the altitude from the given array
        returns:
            the altitude for each timestamp as Numpy array 
        """
        
        #get altitude from gps data 
        alt = self.gps_array[:,2].astype(float)
        
        #round altitude to meters
        self.altitude = savgol_filter(alt, self.window_size, self.polyorder, mode="nearest")
        
        return np.round(self.altitude, 0)

    def get_total_distance(self) -> float:
        """
        takes:
            given Numpy array
        does:
            this method calculates the traveled distance with the use of the Haversine formular.
            It takes into account the given altitude.
        returns:
            calculated total distance in meters. 
        """

        #get distance array with method to use later on 
        self.get_distance()

        #calculte total distance by adding every part 
        totalget_distance = np.sum(self.dist)

        return float(totalget_distance)

    def get_gradient_deg(self) -> np.ndarray:
        """
        takes:
            given Numpy array 
        does:
            Calculates the gradient for each timestamp with the distance and altitude delta 
        returns:
            gradient in degree for each timestamp as Numpy array
        """
        
        #get altitude and distance
        #call distance method for later use
        self.get_distance()
        self.get_altitude()

       
        d_alt = np.diff(self.altitude)

        min_dist = 1.0
        safe_dist_2d = np.where(self.dist_2d < min_dist, min_dist, self.dist_2d)

        #calculate gradient for each timestamp
        #sin(phi) = gegenkat / hypo
        frac = d_alt / safe_dist_2d
        phi = np.rad2deg(np.arctan(frac))   

        #Sicherheitsnetz: realistische Straßen-/Wegsteigungen liegen praktisch nie über
        #±30° (~58%).
        max_gradient_deg = 30.0
        phi = np.clip(phi, -max_gradient_deg, max_gradient_deg)

        #round to .1 degree
        phi_round = np.round(phi, 1)

        return phi_round
    
    def get_gradient_percent(self) -> np.ndarray:
        """
        takes:
            given Numpy array 
        does:
            Calculates the gradient for each timestamp with the distance and altitude delta 
        returns: 
            gradient in percent for each timestamp as Numpy array
        """

        #get altitude and distance
        #call distance method for later use
        self.get_distance()
        self.get_altitude()

        
        d_alt = np.diff(self.altitude)

        #gleicher Mindestabstand wie in get_gradient_deg(), siehe Kommentar dort
        min_dist = 1.0
        safe_dist_2d = np.where(self.dist_2d < min_dist, min_dist, self.dist_2d)

        #calculate gradient for each timestamp
        frac = d_alt / safe_dist_2d

        #transform angle to percent 
        percent = frac * 100 

        #Sicherheitsnetz: ±58% (~30°) als realistisches Maximum, siehe get_gradient_deg()
        max_gradient_percent = 58.0
        percent = np.clip(percent, -max_gradient_percent, max_gradient_percent)

        #round to .1 percent 
        percent_round = np.round(percent, 1)

        return percent_round

    def get_ascent_and_descent(self) -> tuple[float, float]:
        """
        takes:
            given Numpy array 
        does:
            Calculates the total ascent and descent   
        returns: 
            tuple (ascent, descent)
        """
        #get altitude and distance
        self.get_altitude()

        #get height delta for each timestamp
        d_alt = np.diff(self.altitude)

        #calculate the sum of ascent and descent 
        #absolute value for descent to get positive value
        ascent = d_alt[d_alt > 0].sum()
        descent = np.abs(d_alt[d_alt < 0].sum())

        return (np.round(ascent), np.round(descent))

    def get_total_time(self) -> tuple[int, int, int]:
        """
        takes:
            given numpy Array
        does:
            Calculates the total time needed for the given gps track
        returns:
            total elapsed time as tuple (stunden, minuten, sekunden)
        """

        #get first and last timestamp from gps track
        start = self.gps_array[0,3]
        end = self.gps_array[-1,3]

        #calculate elapsed time 
        total = end - start
        
        #in Sekunde
        self.total_time = total.total_seconds() 

        #convert seconds to hours, minutes, seconds 
        stunden = int(self.total_time // 3600)
        minuten = int((self.total_time % 3600) // 60)
        sekunden = int(np.round(self.total_time % 60))
        
        return (stunden, minuten, sekunden)


    def get_mean_speed(self) -> float:
        """
        takes:
            given Numpy Array
        does:
            calculates the mean speed over the whole track
        returns:
            mean speed in km/h 
        """

        #get time and distance 
        self.get_total_time()
        dist = self.get_total_distance()

        #convert to h and km
        dist_km = dist / 1000
        time_h = self.total_time / 3600
        
        return np.round((dist_km / time_h), 2)

    def get_min_max_elevation(self) -> tuple [int, int]:
        """
        takes: 
            given Numpy array with gps data
        does: 
            gets the highest and lowest point of elevation
        returns:
            min and max elevation in meters (min, max)
        """
        #get elevation 
        elevation = self.gps_array[:,2].astype(float)

        #get min and max value 
        min = int(np.round(elevation.min()))
        max = int(np.round(elevation.max()))

        return (min, max)
    
    def get_air_density(self) -> np.ndarray: 
        """
        takes:
            given Numpy array
        does:
            this method calculates the air densitiy for each timestamp in the given GPS Data
        returns:
            Numpy Array with air density [kg/m^3]
        """
        p_0 = 101325 #Luftdruck auf Meereshöhe (ca.) [Pa]
        g = 9.81 #[m/s^2] 
        M = 0.02896 #Molare Masse Luft [kg/mol]
        R = 8.314 #Gaskonstante [J/(mol * K)]
        T = self.gps_array[:,4].astype(float) 
        T_abs = T + 273.15 #Absolte Temperatur (C + 273,15) [K]
        self.get_altitude() #höhe

        x = -((g * M * self.altitude)/(R * T_abs))
        p = p_0 * np.exp(x) #Luftdruck in Paskal [kg^2 / m * s]

        self.rho = (p * M) / (R * T_abs) #Luftdichte [kg/m^3]
        
        #Mittelwerte zwischen Messerwerten, damit es auch 2283 werte sind 
        rho_mittelwerte = (self.rho[:-1] + self.rho[1:]) / 2
        
        return rho_mittelwerte 

    def get_plotting_distance(self) -> np.ndarray: 
        """
        takes:
            given Numpy array
        does:
            this method adds an 0 at the beginning of the get_distance method 
        returns:
            Numpy Array with the same dimension as altitude
        """
        raw_dist = self.get_distance()
        
        #insert a 0 as the first value 
        dist_with_start = np.insert(raw_dist, 0, 0.0)
        
        # np.cumsum calculates running sum 
        cumulative_dist = np.cumsum(dist_with_start)
        
        #return distance in kilometers 
        return cumulative_dist / 1000
