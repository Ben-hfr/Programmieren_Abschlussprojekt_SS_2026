# ---- IMPORTS ---- 
from pathlib import Path

# ---- CUSTOM IMPORTS ---- 

from gui_app import EBikeGUI

# ---- Merge Data Path ----
project_root = Path(__file__).resolve().parent


# ---- mainloop ----
app = EBikeGUI()
app.mainloop()


