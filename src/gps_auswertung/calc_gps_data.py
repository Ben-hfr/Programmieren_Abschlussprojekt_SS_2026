import numpy as np

class Calc_GPS_Data():
    """calculates different values for a given np.array from a gps-csv-file
    
        possble functions are:"""
    def __init__(self, gps_array: np.ndarray):
        
        self.gps_array = gps_array

    def get_total_distance(self) -> float:
        """
        takes: given Numpy array
        does: this method calculates the traveled distance with the use of the Haversine formular.
        It takes into account the given altitude.
        gives: calculated total distance in meters. 
        """

        #Erd Raduis [M]
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

        #calculte total distance by adding every part 
        total_distance = np.sum(distance_3d)

        return float(total_distance)
 
