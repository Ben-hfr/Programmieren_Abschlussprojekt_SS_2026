import numpy as np
import pandas as pd
from pathlib import Path

csv_dir = Path(__file__).resolve().parent

def import_csv_to_array(dateiname: str) -> np.array:
    """give csv-file name;
        imports gps-data as a pandas array;
        [lat][lon][ele][time][temp]
    """
    #fügt den name an den pfad an
    dateipfad = csv_dir / dateiname 

    gps_pandas = pd.read_csv(dateipfad, delimiter=";")

    #convert time in datetime for calculation
    gps_pandas["time"] = pd.to_datetime(gps_pandas["time"])
   
    #convert pandas keyframe to numpy-array
    gps_array = gps_pandas[["lat","lon","ele","time","temperature"]].to_numpy()
    
    return gps_array

if __name__ == "__main__":
    
    array = import_csv_to_array("final_project_input_data.csv")
    print(array[0,:])