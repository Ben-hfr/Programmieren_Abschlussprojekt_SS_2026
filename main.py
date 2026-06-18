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

#merge Data path
project_root = Path(__file__).resolve().parent


array = import_csv_to_array("final_project_input_data.csv")
print(array[0,:])
