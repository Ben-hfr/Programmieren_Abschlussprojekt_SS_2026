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

from matplotlib.figure import Figure
#imports for Tkinter to mate plt-figures into Tk-widgets
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

try:
    import importlib
    tkinterdnd2 = importlib.import_module("tkinterdnd2")
    DND_FILES = tkinterdnd2.DND_FILES
    TkinterDnD = tkinterdnd2.TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

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
        self.geometry("1200x750")
        
        self.csv_path: Path | None = None
        self.gps_evaluator = None
        self.force_calc = None
        self.motor_calc = None
        
        self.build_layout()
        
        
#=====================================================
    def build_layout(self):

# ---- Statuszeile ----
        self.status_var = tk.StringVar(value="Bereit. Bitte CSV-Datei laden.")
        status_bar = ttk.Label(textvariable=self.status_var, anchor="w", relief="sunken")
        status_bar.pack(side="bottom", fill="x")        

# ---- linke Spalte: Drop Zone, Parameter, Ergebnisse ----
        left = ttk.Frame(padding=10)
        left.pack(side="left",fill="y")
        
        self.build_drop_zone(left)
        
# ---- rechte Spalte: Plots in Tabs ----
        right = ttk.Frame(padding=10)
        right.pack(side="right", fill="both", expand=True)
 
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)
 
        self.tab_gps = ttk.Frame(self.notebook)
        self.tab_motor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gps, text="Höhe / Leistung / Geschwindigkeit")
        self.notebook.add(self.tab_motor, text="Motor (Drehmoment / Strom)")
 
        self.fig_gps, self.canvas_gps = self._make_canvas(self.tab_gps, n_axes=3)
        self.fig_motor, self.canvas_motor = self._make_canvas(self.tab_motor, n_axes=2)
        
      
    #Achsen für Plots  
    def _make_canvas(self, parent, n_axes: int):
        fig = Figure(figsize=(7, 7), dpi=100)
        for i in range(n_axes):
            fig.add_subplot(n_axes, 1, i + 1)
            #makes figure into a widget for Tk
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        return fig, canvas
    
    #Datei per D&D oder Auswahl hinzufügen
    def build_drop_zone(self, parent):
        box = ttk.LabelFrame(parent, text="CSV-Datei", padding=10)
        box.configure(width=250)
        box.pack(fill="x", pady=(0,10))

        if DND_AVAILABLE:
            hint = "CSV hierhin ziehen"
        else:
            hint = "Drag & Drop nicht verfügbar"
        
        self.drop_label = tk.Label(box, text=f"{hint} \n (oder Klicken zum Auswählen)", 
                                   width= 32, height= 4, relief="ridge", bg="#F5F5DC", justify="center" )

        self.drop_label.pack(fill="x")
        
        #Funktion des Knopfes binden
        self.drop_label.bind("<Button-1>", lambda e: self._browse_file())
 
        #erstellt D&D zone für Betriebssystem
        if DND_AVAILABLE:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
        else:
            note = ttk.Label(
                box, foreground="gray",
                text="Tipp: 'pip install tkinterdnd2' für Drag & Drop",
                wraplength=260
            )
            note.pack(fill="x", pady=(5, 0))
 
        #shows the Name of file if loaded
        self.file_label_var = tk.StringVar(value="Keine Datei geladen")
        ttk.Label(box, textvariable=self.file_label_var, foreground="blue").pack(fill="x", pady=(5, 0))
        
    #=================================================
    #EVENTS
    
    def _browse_file(self):
        #opens standart File-Browser and saves the path into path_str
        path_str = filedialog.askopenfilename(
            title="GPS-CSV auswählen",
            filetypes=[("CSV-Dateien", "*.csv")], #only CSV!
        )
        #checks if user pressed cancel button. Only if Path_str is a Path the file gets loaded
        if path_str:
            #path_str gets converted into a real Path
            self._load_file(Path(path_str))
 
    def _load_file(self, path: Path):
        if path.suffix.lower() != ".csv":
            messagebox.showerror("Falscher Dateityp", "Bitte eine .csv-Datei auswählen.")
            return
 
        #path gets saved for later functions
        self.csv_path = path
        #updates name for the UI
        self.file_label_var.set(path.name)
        #self.calc_button.config(state="normal")
        #updates the statuslabe (bottom of the GUI)
        self.status_var.set(f"Datei geladen: {path.name}. Bereit zur Berechnung.")
        
 


if __name__ == "__main__":

    app = EBikeGUI()
    app.mainloop()