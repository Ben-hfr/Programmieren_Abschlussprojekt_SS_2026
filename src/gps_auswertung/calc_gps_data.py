import numpy as np

class Calc_GPS_Data():
    """calculates different values for a given np.array from a gps-csv-file
    
        possble functions are:"""
    def __init__(self, gps_array: np.ndarray):
        
        self.gps_array = gps_array
        self.dist = 0

    def _distance(self) -> float:

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
        distance_3d = np.sqrt((distance_2d**2) + (dalt**2))

        self.dist = distance_3d

    
    def get_total_distance(self) -> float:
        """
        takes: given Numpy array
        does: this method calculates the traveled distance with the use of the Haversine formular.
        It takes into account the given altitude.
        gives: calculated total distance in meters. 
        """

        #get distance array with method to use later on 
        self._distance()

        #calculte total distance by adding every part 
        total_distance = np.sum(self.dist)

        return float(total_distance)
    
    def get_speed(self) -> np.ndarray:
        """
        takes: given Numpy array
        does: this method calculates the velocity for each time delta in the given GPS Data
        gives: calculates the velocity in kmh 
        """
        
        #get distance array with method to use later on 
        self._distance()

        #get time and distance 
        distance = self.dist
        time = self.gps_array[:,3]

        #calculate time delta 
        dtime = np.diff(time)

        #convert time deltas to seconds
        dt_seconds = dtime.astype('timedelta64[s]').astype(float)

        #calculate speed
        dt_seconds = np.where(dt_seconds == 0, 1e-5, dt_seconds)
        speed_ms = distance / dt_seconds

        #convert to km/h
        speed_kmh = speed_ms * 3.6

        return speed_kmh