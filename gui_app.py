"""
gui_app.py
==========

Tkinter-GUI für die E-Bike Simulation

Funktionen:
    - CSV-Datei per Drag & Drop ODER per Klick laden
    - Parameter (Filter, Masse, cw*A, Radgröße, Motorkonstante) einstellen
    - Wichtige Kennzahlen auf einen Blick sehen (Distanz, Zeit, Geschwindigkei, Höhenmeter)
    - Eingebettete Plots
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font

import matplotlib as plt

from tkinterdnd2 import DND_FILES, TkinterDnD

#--------------------
project_root = Path(__file__).resolve().parent

from src.gps_auswertung.calc_gps_data import Calc_GPS_Data
from src.gps_auswertung.calc_force_data import Calc_Force_Data
from src.gps_auswertung.calc_motor_data import Calc_Motor_Data


def import_csv_to_array(file_path: Path) -> np.array:
    """give csv-file name;
        imports gps-data as a pandas array;
        [lat][lon][ele][time][temp]
    """
    #prüfung ob Pfad = global
    if not file_path.absolute():
        file_path = file_path.resolve() #Macht zu einem globalen Pfad

    gps_pandas = pd.read_csv(file_path, delimiter=";")

    #convert time in datetime for calculation
    gps_pandas["time"] = pd.to_datetime(gps_pandas["time"])
    
    # Resampling: timedelta 1s 
    # Set time to temporary index
    gps_pandas.set_index("time", inplace=True)

    # resample to 1 second('1s')
    # every gap is filled liniearly 
    gps_pandas_resampled = gps_pandas.resample('1s').interpolate(method='linear')

    # if there are NaNs ad the edges
    gps_pandas_resampled.bfill(inplace=True)  # Backward fill
    gps_pandas_resampled.ffill(inplace=True)  # Forward fill

    # Reset time index to normal colum
    gps_pandas_resampled.reset_index(inplace=True)
   
    #convert pandas keyframe to numpy-array
    gps_array = gps_pandas_resampled[["lat", "lon", "ele", "time", "temperature"]].to_numpy()
    
    return gps_array


class EBikeGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("E-Bike Simulation")
        self.geometry("500x500")
    

if __name__ == "__main__":

    app = EBikeGUI()
    app.mainloop()