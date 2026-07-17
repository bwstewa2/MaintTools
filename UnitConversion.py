import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Conversions.pressure as con_pressure

class UnitConversion_Panel:
    def __init__(self):
        self.input_pressure = ttk.StringVar(value=f"{0:.3e}")
        self.output_pressure = ttk.StringVar(value=f"{0:.3e}")
        self.input_pressure_units = ttk.StringVar(value="Torr")
        self.output_pressure_units = ttk.StringVar(value="Torr")

    def create(self, tab):
        #Pressure
        ttk.Label(tab, text="Pressure:").grid(row=0, column=0, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.input_pressure, width=25)
        self.input_pressure_entry.grid(row=0, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.in_pressure_units_cb = ttk.Combobox(tab, textvariable=self.input_pressure_units, values=con_pressure.pressure_units, width=25)
        self.in_pressure_units_cb.grid(row=0, column=2, padx=10, pady=(10,0), sticky='nsew')
        ttk.Label(tab, text="to").grid(row=0, column=3, padx=10, pady=(10,0), sticky='nsew')
        self.out_pressure_units_cb = ttk.Combobox(tab, textvariable=self.output_pressure_units, values=con_pressure.pressure_units, width=25)
        self.out_pressure_units_cb.grid(row=0, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.output_pressure, width=25)
        self.input_pressure_entry.grid(row=0, column=5, padx=10, pady=(10,0), sticky='nsew')
        pressure_calc_btn = ttk.Button(tab, text="Submit", command=self.calc_pressure)
        pressure_calc_btn.grid(row=0, column=6, padx=10, pady=(10,0), sticky='nsew')

        self.output_pressure.trace_add("write", self.update_sci_not)

    def update_sci_not(self, *args):
        self.output_pressure.set(f"{float(self.output_pressure.get()):.3e}")
    
    def calc_pressure(self, event=None):
        self.output_pressure.set(con_pressure.convert_pressure(self.input_pressure_units.get(), self.output_pressure_units.get(), self.input_pressure.get()))
        
       

       