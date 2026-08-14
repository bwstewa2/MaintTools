import platform
import ctypes

import ttkbootstrap as ttk
from tkinter.font import nametofont

import Delta.DeltaConstants as dc
from Delta.Delta import Delta_Panel
from Leakback.Leakback import Leakback_Panel
from ParameterCheck.ParameterCheck import Parameter_Panel
from AnalogCalibration.AnalogCalibration import AnalogCalibration_Panel
from Targets.TargetWear import TargetWear_Panel
from Conversions.UnitConversion import UnitConversion_Panel

def configure_dpi():
    """Configure DPI awareness based on the current operating system."""
    system = platform.system()
    if system == "Windows":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except AttributeError:
            ctypes.windll.user32.SetProcessDPIAware()
    elif system == "Darwin":
        root.tk.call("tk", "scaling", 2.0)


def configure_font():
    """Set the application-wide default font."""
    default_font = nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10, weight="normal")


def build_menubar():
    """Build and return the application menu bar."""
    menubar = ttk.Menu(root)
    file_menu = ttk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="ReadMe", command=dc.open_about)
    file_menu.add_command(label="History", command=dc.open_history)
    file_menu.add_command(label="Settings", command=dc.open_settings)
    menubar.add_cascade(label="File", menu=file_menu)
    return menubar


def build_notebook(panels: dict) -> ttk.Notebook:
    """Create and populate the notebook with panel tabs."""
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")
    for name, panel in panels.items():
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=name)
        panel.create(tab)
    return notebook


def on_closing():
    """Handle application close event."""
    PANELS["Delta"].on_closing()
    root.quit()
    root.destroy()


# ------------------------------------------------------------------ #
#  Main                                                                #
# ------------------------------------------------------------------ #
root = ttk.Window(themename="solar", title="MaintTools")

PANELS = {
    "Leakback": Leakback_Panel(),
    "Parameters Check": Parameter_Panel(),
    "Target Wear": TargetWear_Panel(),
    "Delta": Delta_Panel(),
    "Analog Calibration": AnalogCalibration_Panel(),
    "Unit Conversion": UnitConversion_Panel(),
}

configure_dpi()
configure_font()

build_notebook(PANELS)
root.config(menu=build_menubar())
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()