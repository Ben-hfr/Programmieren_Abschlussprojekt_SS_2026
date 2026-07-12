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
        
        self._build_drop_zone(left)
        self._build_parameter_form(left)
        self._build_results_box(left)
        
# ---- rechte Spalte: Plots in Tabs ----
        right = ttk.Frame(padding=10)
        right.pack(side="right", fill="both", expand=True)
 
        #Notebooks für verschiedene Tabs
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)
 
        self.tab_gps = ttk.Frame(self.notebook)
        self.tab_motor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_gps, text="Höhe / Leistung / Geschwindigkeit")
        self.notebook.add(self.tab_motor, text="Motor (Drehmoment / Strom)")
        #Achsen für spätere Plots
        self.fig_gps, self.canvas_gps = self._make_canvas(self.tab_gps, n_axes=3)
        self.fig_motor, self.canvas_motor = self._make_canvas(self.tab_motor, n_axes=2)
        
      
    #Achsen für Plots  
    def _make_canvas(self, parent, n_axes: int):
        fig = Figure(figsize=(7, 7), dpi=100)
        for i in range(n_axes):
            fig.add_subplot(n_axes, 1, i + 1)
            #Wandelt matplotlib figuren in Tkinter widgets um
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        return fig, canvas
    
    #Datei per D&D oder Auswahl hinzufügen
    def _build_drop_zone(self, parent):
        box = ttk.LabelFrame(parent, text="CSV-Datei", padding=10)
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
 
        #Zeigt den Name der geladenen Datei
        self.file_label_var = tk.StringVar(value="Keine Datei geladen")
        ttk.Label(box, textvariable=self.file_label_var, foreground="blue").pack(fill="x", pady=(5, 0))
        
    #Parameter
    def _build_parameter_form(self,parent):
        box = ttk.LabelFrame(parent, text="Parameter", padding=10)
        box.pack(fill="x", pady=(0,10))
        
        self.params = {}
        #Standart-Variablen für alle möglichen Parameter (Technischer Name - Wert - GUI Name)
        defaults = [
            ("window_size", "21", "Filter-Fenstergröße (ungerade)"),
            ("polyorder", "3", "Filter-Polynomgrad"),
            ("mass_rider", "70.0", "Fahrergewicht [kg]"),
            ("mass_bike", "15.0", "Fahrradgewicht [kg]"),
            ("cw_times_area", "0.5625", "cw * Stirnfläche [m²]"),
            ("c_roll", "0.0", "Rollwiderstandsbeiwert [-]"),
            ("d_wheel", "27", "Laufraddurchmesser [Zoll]"),
            ("k_m", "1.5", "Motorkonstante [Nm/A]"),
        ]
        
        #Tabelle erstellen und mit standartwerten füllen (es sind StringVar und können jederzeit verändert werden)
        for i, (key, default, desc) in enumerate(defaults):
            ttk.Label(box, text=desc).grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            entry = ttk.Entry(box, textvariable=var, width=10)
            entry.grid(row=i, column=1, sticky="e", pady=2)
            self.params[key] = var
 
        box.columnconfigure(0, weight=1)
 
        #Knopf für starten der Berechnung
        self.calc_button = ttk.Button(
            box, text="Berechnen", command=self._run_calculation, state="disabled"
        )
        self.calc_button.grid(row=len(defaults), column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        #selbsterklärend
    def _build_results_box(self, parent):
        box = ttk.LabelFrame(parent, text="Ergebnisse", padding=10)
        box.pack(fill="both", expand=True)
 
        self.results_text = tk.Text(box, width=38, height=18, state="disabled",
                                     wrap="word", font=("Consolas", 9))
        self.results_text.pack(fill="both", expand=True)
        
    #=================================================
    #EVENTS
    
    #Filebrowser öffnen
    def _browse_file(self):
        #Öffnet den Filebrowser vom Betriebssystem
        path_str = filedialog.askopenfilename(
            title="GPS-CSV auswählen",
            filetypes=[("CSV-Dateien", "*.csv")], #only CSV!
        )
        #Nur wenn tatsächlich eine Datei ausgewählt wurde, wird load_file ausgeführt
        if path_str:
            #path_str wird zu einem Path-Objekt umgewandelt
            self._load_file(Path(path_str))
 
    #laden einer CSV-Datei
    def _load_file(self, path: Path):
        if path.suffix.lower() != ".csv":
            messagebox.showerror("Falscher Dateityp", "Bitte eine .csv-Datei auswählen.")
            return
 
        #path wird gespeichert
        self.csv_path = path
        #Name wird geupdated für GUI
        self.file_label_var.set(path.name)
        self.calc_button.config(state="normal") #when a file is loaded you can click the calculate button
        #Statusleiste wird geupdated
        self.status_var.set(f"Datei geladen: {path.name}. Bereit zur Berechnung.")
        
    
    #liest alle parameter aus dem parameterfeld
    def _read_params(self):
        try:
            return dict(
                window_size=int(self.params["window_size"].get()),
                polyorder=int(self.params["polyorder"].get()),
                mass_rider=float(self.params["mass_rider"].get()),
                mass_bike=float(self.params["mass_bike"].get()),
                cw_times_area=float(self.params["cw_times_area"].get()),
                c_roll=float(self.params["c_roll"].get()),
                d_wheel=float(self.params["d_wheel"].get()),
                k_m=float(self.params["k_m"].get()),
            )
        except ValueError as e:
            raise ValueError(f"Ungültiger Parameterwert: {e}")
 
    #berechnet alle Werte der mithilfe der erstellten Klassen
    def _run_calculation(self):
        if self.csv_path is None:
            messagebox.showwarning("Keine Datei", "Bitte zuerst eine CSV-Datei laden.")
            return
        
        try:
            p = self._read_params()
            self.status_var.set("Berechne ...")
            self.update_idletasks() #um "Berechne..." sofort anzuzeigen
 
            gps_array = import_csv_to_array(self.csv_path)
 
            #selbst erstellte Klassen instanzieren
            self.gps_evaluator = Calc_GPS_Data(gps_array, p["window_size"], p["polyorder"]) 
            self.force_calc = Calc_Force_Data(
                self.gps_evaluator,
                mass_rider=p["mass_rider"],
                mass_bike=p["mass_bike"],
                cw_times_area=p["cw_times_area"],
                c_roll=p["c_roll"],
            )
            self.motor_calc = Calc_Motor_Data(
                self.force_calc, d_wheel=p["d_wheel"], k_m=p["k_m"]
            )
 
            self._update_results()
            self._update_plots()
            self.status_var.set("Berechnung abgeschlossen.")
            
        except Exception as e:
            messagebox.showerror("Fehler bei der Berechnung", str(e))
            self.status_var.set("Fehler bei der Berechnung.")
    
    def _update_results(self):
        g = self.gps_evaluator
        f = self.force_calc
        m = self.motor_calc
 
        #Berechnungen
        distance = g.get_total_distance()
        h, mi, s = g.get_total_time()
        ascent, descent = g.get_ascent_and_descent()
        min_ele, max_ele = g.get_min_max_elevation()
        mean_speed = g.get_mean_speed()
        max_power = float(np.max(f.get_power()))
        mean_power = float(np.mean(f.get_power()))
        max_torque = float(np.max(m.get_torque()))
        max_current = float(np.max(m.get_motor_current()))


        
        lines = [
            f"Gesamtdistanz:     {distance/1000:.2f} km",
            f"Gesamtzeit:        {h:02d}:{mi:02d}:{s:02d}",
            f"Mittl. Geschw.:    {mean_speed:.2f} km/h",
            "",
            f"Anstieg:           {ascent:.0f} m",
            f"Abstieg:           {descent:.0f} m",
            f"Min. Höhe:         {min_ele} m",
            f"Max. Höhe:         {max_ele} m",
            "",
            f"Ø Leistung:        {mean_power:.1f} W",
            f"Max. Leistung:     {max_power:.1f} W",
            "",
            f"Max. Drehmoment:   {max_torque:.2f} Nm",
            f"Max. Motorstrom:   {max_current:.2f} A",
        ]
        
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "\n".join(lines))
        self.results_text.config(state="disabled")
        
    def _update_plots(self):
        g = self.gps_evaluator
        f = self.force_calc
        m = self.motor_calc
 
        x_full = g.get_plotting_distance()
        x_delta = x_full[1:]
 
        # --- Tab 1: Höhe / Leistung / Geschwindigkeit ---
        ax1, ax2, ax3 = self.fig_gps.axes
        for ax in (ax1, ax2, ax3):
            ax.clear()
        ax1.margins(x=0)
        ax1.plot(x_full, g.get_altitude(), color="tab:green")
        ax1.set_ylabel("Höhe [m]")
        ax1.set_title("Höhenprofil")

        ax2.margins(x=0)
        ax2.plot(x_delta, f.get_power(), color="tab:red")
        ax2.set_ylabel("Leistung [W]")
        ax2.set_title("Benötigte Leistung")
 
        ax3.margins(x=0)
        ax3.plot(x_delta, g.get_speed(), color="tab:blue")
        ax3.set_ylabel("Geschw. [km/h]")
        ax3.set_xlabel("Distanz [km]")
        ax3.set_title("Geschwindigkeit")
 
        self.fig_gps.tight_layout()
        self.canvas_gps.draw()
 
        # --- Tab 2: Motor ---
        ax4, ax5 = self.fig_motor.axes
        for ax in (ax4, ax5):
            ax.clear()
 
        ax4.plot(x_delta, m.get_torque(), color="tab:purple")
        ax4.set_ylabel("Drehmoment [Nm]")
        ax4.set_title("Drehmoment am Antriebsrad")
 
        ax5.plot(x_delta, m.get_motor_current(), color="tab:orange")
        ax5.set_ylabel("Strom [A]")
        ax5.set_xlabel("Distanz [m]")
        ax5.set_title("Motorstrom")
 
        self.fig_motor.tight_layout()
        self.canvas_motor.draw()
    
    
        
if __name__ == "__main__":

    app = EBikeGUI()
    app.mainloop()