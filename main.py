# ---- IMPORTS ----
import sys
import logging
from pathlib import Path


# ----CUSTOM IMPORTS ----

from gui_app import EBikeGUI

# ---- PATH FIX ----
project_root = Path(__file__).resolve().parent

# ---- LOGGING ----

#setup logging
log_dir = project_root / "logs"

def setup_logging():
    # 2. Ordner erstellen, falls er noch nicht existiert
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Pfad für die eigentliche Log-Datei definieren
    log_file_path = log_dir / "simulation_run.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # 3. Hier nutzen wir nun den dynamischen Pfad statt nur dem Dateinamen
            logging.FileHandler(log_file_path, encoding="utf-8")
        ]
    )
#logging for Matplotlib 
logging.getLogger("matplotlib").setLevel(logging.WARNING) 

setup_logging()

# ---- MAINLOOP ----
app = EBikeGUI()
app.mainloop()
