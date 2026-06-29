import numpy as np
import pandas as pd
import math
import os
import sys
import unittest
import matplotlib.pyplot as plt
from abc import ABC
from pathlib import Path

#custom imports

from data.csv_to_array import import_csv_to_array
from src.gps_auswertung.calc_gps_data import Calc_GPS_Data
from src.gps_auswertung.calc_force_data import Calc_Force_Data
from src.gps_auswertung.calc_motor_data import Calc_Motor_Data
#merge Data path
project_root = Path(__file__).resolve().parent

#vorläufige Tests
array = import_csv_to_array("final_project_input_data.csv")


#filter 5,4 
gps_evaluator = Calc_GPS_Data(array, 21, 3)
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

print(f"Air density: {gps_evaluator.get_air_density()}")

#beispiel Kräfte
force_calc = Calc_Force_Data(gps_evaluator, mass_rider=70.0, mass_bike=15.0, cw_times_area=0.5625)
 
print(f"req. Force: {force_calc.get_required_force()}N")
print(f"req. power: {force_calc.get_power()}W")

#beispielmotor
motor_calc = Calc_Motor_Data(force_calc, d_wheel=27, k_m=1.5) #r_wheel = 27 inch. Umrechnung muss noch in der Klasse eingebaut werden
 
print(f"torque: {motor_calc.get_torque()}Nm")
print(f"motor-current: {motor_calc.get_motor_current()}A")

fig, ax = plt.subplots()

ax.plot(
    gps_evaluator.get_altitude()
)


plt.show()