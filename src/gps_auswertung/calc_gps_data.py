import numpy as np

class Calc_GPS_Data():
    """calculates different values for a given np.array from a gps-csv-file
    
        possble functions are:"""
    def __init__(self, gps_array: np.ndarray):
        
        self.gps_array = gps_array
        self.dist = 0
        self.speed_ms = 0
        self.acc = 0
        self.altitude = 0
        self.total_time = 0

        #get time
        time = self.gps_array[:,3]
        #calculate time delta 
        dtime = np.diff(time)
        #convert time deltas to seconds
        self.dtime_sec = dtime.astype('timedelta64[s]').astype(float)


    def get_distance(self) -> float:
        """
        takes:
            given Numpy array of GPS-Data
        does:
            this method calculates the distance for each time delta in the given GPS Data and saves it as self.dist
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

        #3D Distance with altitude 
        self.dist = np.sqrt((distance_2d**2) + (dalt**2))

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

        #get time and distance 
        distance = self.dist

        #calculate speed
        self.dtime_sec = np.where(self.dtime_sec == 0, 1e-5, self.dtime_sec)
        self.speed_ms = distance / self.dtime_sec

        #convert to km/h
        self.speed_ms

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

        #calculate acceleration
        self.acc = self.speed_ms / self.dtime_sec

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
        self.altitude = np.round(alt, 0)

        return self.altitude

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
        alt = self.gps_array[:,2].astype(float)


        #get height delta for each timestamp
        d_alt = np.diff(alt)

        #calculate gradient for each timestamp
        #sin(phi) = gegenkat / hypo
        frac = d_alt / self.dist
        phi = np.rad2deg(np.arcsin(frac))   

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
        alt = self.gps_array[:,2].astype(float)

        #get height delta for each timestamp
        d_alt = np.diff(alt)

        #calculate gradient for each timestamp
        #sin(phi) = gegenkat / hypo
        frac = d_alt / self.dist
        phi = np.arcsin(frac) 

        #transform angle to percent 
        percent = np.tan(phi) * 100 

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
        #get altitude
        alt = self.gps_array[:,2].astype(float)

        #calculate altitude delta 
        d_alt = np.diff(alt)

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
        
