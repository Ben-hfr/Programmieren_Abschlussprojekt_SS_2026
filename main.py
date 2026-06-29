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
from src.gps_auswertung.calc_force_data import Calc_Force_Data
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


force_calc = Calc_Force_Data(gps_evaluator, mass=95.0, cw=0.9, area=0.5)
 
print(f"req. Force: {force_calc.get_required_force()}")
print(f"req. power: {force_calc.get_power()}")

