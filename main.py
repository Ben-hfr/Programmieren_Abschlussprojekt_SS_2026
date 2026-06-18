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


array = import_csv_to_array("final_project_input_data.csv")

gps_evaluator = Calc_GPS_Data(array)
distance = gps_evaluator.get_total_distance()
print(distance)
