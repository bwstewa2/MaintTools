import ttkbootstrap as ttk
from tkinter.font import nametofont
from Leakback import Leakback_Panel
from ParameterCheck import Parameter_Panel
from AnalogCalibration import AnalogCalibration_Panel
from TargetWear import TargetWear_Panel
from Delta.Delta import Delta_Panel
import Delta.DeltaConstants as dc
import ctypes
import platform

root = ttk.Window(themename="solar", title="MaintTools")

if platform.system() == 'Windows':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        ctypes.windll.user32.SetProcessDPIAware()
if platform.system() == 'Darwin':
    root.tk.call('tk', 'scaling', 2.0)

default_font = nametofont("TkDefaultFont")
default_font.configure(family="Segoe UI", size=10, weight="normal")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")
menubar = ttk.Menu(root)
file = ttk.Menu(menubar, tearoff = 0) 
menubar.add_cascade(label ='File', menu = file) 
file.add_command(label ='ReadMe', command = dc.open_about) 
file.add_command(label ='History', command = dc.open_history) 
file.add_command(label ='Settings', command = dc.open_settings) 

panels = {
    "Leakback": Leakback_Panel(), 
    "Parameters Check": Parameter_Panel(), 
    "Target Wear": TargetWear_Panel(), 
    "Delta": Delta_Panel(), 
    "Analog Calibration": AnalogCalibration_Panel()
    }

for name, panel in panels.items():
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=name)
    panel.create(tab)

root.config(menu = menubar) 
root.resizable(False, False)

def on_closing():
    panels["Delta"].on_closing()
    root.quit()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

