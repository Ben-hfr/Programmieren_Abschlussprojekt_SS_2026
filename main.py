import numpy as np
import pandas as pd
import math
import os
import sys
import unittest
import matplotlib as mpl
from abc import ABC
from pathlib import Path

#custom imports

from data.csv_to_array import import_csv_to_array
from src.gps_auswertung.calc_gps_data import Calc_GPS_Data
#merge Data path
project_root = Path(__file__).resolve().parent

#vorläufige Tests
array = import_csv_to_array("final_project_input_data.csv")

gps_evaluator = Calc_GPS_Data(array)
distance = gps_evaluator.get_total_distance()
print(distance)

print(f"Speed:{gps_evaluator.get_speed()}")

print(f"Acc:{gps_evaluator.get_acceleration()}")

print(f"timedeltas_sec:{gps_evaluator.dtime_sec}")

print(f"alt:{gps_evaluator.get_altitude()}")

print(f"the total ascent was: {gps_evaluator.get_ascent_and_descent()[0]}m and {gps_evaluator.get_ascent_and_descent()[1]}m descent")

print(f"the total elapsed time was: {gps_evaluator.get_total_time()}")

print(f"mean speed: {gps_evaluator.get_mean_speed()}km/h")

print(f"lowest point: {gps_evaluator.get_min_max_elevation()[0]}m. Highest point: {gps_evaluator.get_min_max_elevation()[1]}m")
#gradient = gps_evaluator.get_gradient_deg()
#np.set_printoptions(threshold=np.inf)
#print(gradient)

#gradient_percent = gps_evaluator.get_gradient_percent()
#np.set_printoptions(threshold=np.inf)
#print(gradient_percent)
