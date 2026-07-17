import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Conversions.pressure as con_pressure

class UnitConversion_Panel:
    def __init__(self):
        self.input = ttk.StringVar(value=f"{0:.3e}")
        self.output = ttk.StringVar(value=f"{0:.3e}")
        self.in_pressure = ttk.StringVar(value="Torr")
        self.out_pressure = ttk.StringVar(value="Torr")
        self.pressure_units = ["Torr", "mTorr", "Bar", "mBar", "Pa", "mPa", "inHg", "psi", "atm"]

    def create(self, tab):
        #Pressure
        ttk.Label(tab, text="Pressure:").grid(row=0, column=0, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.input, width=25)
        self.input_pressure_entry.grid(row=0, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.input_units_cb = ttk.Combobox(tab, textvariable=self.in_pressure, values=self.pressure_units, width=25)
        self.input_units_cb.grid(row=0, column=2, padx=10, pady=(10,0), sticky='nsew')
        output_label = ttk.Label(tab, text="to")
        output_label.grid(row=0, column=3, padx=10, pady=(10,0), sticky='nsew')
        self.output_units_cb = ttk.Combobox(tab, textvariable=self.out_pressure, values=self.pressure_units, width=25)
        self.output_units_cb.grid(row=0, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.output, width=25)
        self.input_pressure_entry.grid(row=0, column=5, padx=10, pady=(10,0), sticky='nsew')
        calc_btn = ttk.Button(tab, text="Submit", command=self.calc_pressure)
        calc_btn.grid(row=0, column=6, padx=10, pady=(10,0), sticky='nsew')

        self.output.trace_add("write", self.update_sci_not)

    def update_sci_not(self, *args):
        self.output.set(f"{float(self.output.get()):.3e}")
    
    def calc_pressure(self, event=None):
        in_type = self.in_pressure.get()
        out_type = self.out_pressure.get()
        
        in_pressure = 0
        try:
            in_pressure = float(self.input.get())
        except ValueError:
            self.input.set(0)
            return
        
        if in_type[0] == 'm' and out_type[0] != 'm':
            in_pressure = con_pressure.toNom(in_pressure)
            in_type = in_type[1:]
        elif in_type[0] != 'm' and out_type[0] == 'm':
            in_pressure = con_pressure.toMilli(in_pressure)
            out_type = out_type[1:]
        elif in_type[0] == 'm' and out_type[0] == 'm':
            in_type = in_type[1:]
            out_type = out_type[1:]
        self.output.set(in_pressure)

        if in_type == "Torr":
            if out_type == "Bar":
                self.output.set(con_pressure.torrToBar(in_pressure))
            elif out_type == "Pa":
                self.output.set(con_pressure.torrToPa(in_pressure))
            elif out_type == "inHg":
                self.output.set(con_pressure.torrToInhg(in_pressure))
            elif out_type == "psi":
                self.output.set(con_pressure.torrToPsi(in_pressure))
            elif out_type == "atm":
                self.output.set(con_pressure.torrToAtm(in_pressure))
        elif in_type == "Bar":
            if out_type == "Torr":
                self.output.set(con_pressure.barToTorr(in_pressure))
            elif out_type == "Pa":
                self.output.set(con_pressure.barToPa(in_pressure))
            elif out_type == "inHg":
                self.output.set(con_pressure.barToInhg(in_pressure))
            elif out_type == "psi":
                self.output.set(con_pressure.barToPsi(in_pressure))
            elif out_type == "atm":
                self.output.set(con_pressure.barToAtm(in_pressure))
        elif in_type == "Pa":
            if out_type == "Torr":
                self.output.set(con_pressure.paToTorr(in_pressure))
            elif out_type == "Bar":
                self.output.set(con_pressure.paToBar(in_pressure))
            elif out_type == "inHg":
                self.output.set(con_pressure.paToInhg(in_pressure))
            elif out_type == "psi":
                self.output.set(con_pressure.paToPsi(in_pressure))
            elif out_type == "atm":
                self.output.set(con_pressure.paToAtm(in_pressure))
        elif in_type == "inHg":
            if out_type == "Torr":
                self.output.set(con_pressure.inhgToTorr(in_pressure))
            elif out_type == "Bar":
                self.output.set(con_pressure.inhgToBar(in_pressure))
            elif out_type == "Pa":
                self.output.set(con_pressure.inhgToPa(in_pressure))
            elif out_type == "psi":
                self.output.set(con_pressure.inhgToPsi(in_pressure))
            elif out_type == "atm":
                self.output.set(con_pressure.inhgToAtm(in_pressure))
        elif in_type == "psi":
            if out_type == "Torr":
                self.output.set(con_pressure.psiToTorr(in_pressure))
            elif out_type == "Bar":
                self.output.set(con_pressure.psiToBar(in_pressure))
            elif out_type == "Pa":
                self.output.set(con_pressure.psiToPa(in_pressure))
            elif out_type == "inHg":
                self.output.set(con_pressure.psiToInhg(in_pressure))
            elif out_type == "atm":
                self.output.set(con_pressure.psiToAtm(in_pressure))
        elif in_type == "atm":
            if out_type == "Torr":
                self.output.set(con_pressure.atmToTorr(in_pressure))
            elif out_type == "Bar":
                self.output.set(con_pressure.atmToBar(in_pressure))
            elif out_type == "Pa":
                self.output.set(con_pressure.atmToPa(in_pressure))
            elif out_type == "inHg":
                self.output.set(con_pressure.atmToInhg(in_pressure))
            elif out_type == "psi":
                self.output.set(con_pressure.atmToPsi(in_pressure))