import numpy as np
import pandas as pd

def import_csv_to_array(dateipfad: str) -> np.array:
    """give path to csv-file;
        imports gps-data as a pandas array;
        [lat][lon][ele][time][temp]
    """
    gps_pandas = pd.read_csv(dateipfad, delimiter=";")
   
    #convert pandas keyframe to numpy-array
    gps_array = gps_pandas.to_numpy()
    
    return gps_array

if __name__ == "__main__":
    
    array = import_csv_to_array("data/final_project_input_data.csv")
    print(array[0,:])