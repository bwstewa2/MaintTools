import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Conversions.pressure as con_pressure
import Conversions.length as con_length
import Conversions.weight as con_weight

DEFAULT_PRESSURE = "Torr"
DEFAULT_LENGTH = "km"
DEFAULT_WEIGHT = "kg"
DEFAULT_IO = f"{0:.3e}"

class UnitConversion_Panel:
    """Panel for converting common units."""
    def __init__(self):
        self._init_vars()

    def _init_vars(self):
        """Initialize all tkinter control variables."""
        self.input_pressure = ttk.StringVar(value=DEFAULT_IO)
        self.output_pressure = ttk.StringVar(value=DEFAULT_IO)
        self.input_pressure_units = ttk.StringVar(value=DEFAULT_PRESSURE)
        self.output_pressure_units = ttk.StringVar(value=DEFAULT_PRESSURE)

        self.input_length = ttk.StringVar(value=DEFAULT_IO)
        self.output_length = ttk.StringVar(value=DEFAULT_IO)
        self.input_length_units = ttk.StringVar(value=DEFAULT_LENGTH)
        self.output_length_units = ttk.StringVar(value=DEFAULT_LENGTH)

        self.input_weight = ttk.StringVar(value=DEFAULT_IO)
        self.output_weight = ttk.StringVar(value=DEFAULT_IO)
        self.input_weight_units = ttk.StringVar(value=DEFAULT_WEIGHT)
        self.output_weight_units = ttk.StringVar(value=DEFAULT_WEIGHT)

    def create(self, tab):
        """Build and grid all widgets into the provided tab frame."""
        self._build_pressure_row(tab)
        self._build_length_row(tab)
        self._build_weight_row(tab)
        self._bind_events()

    def _build_pressure_row(self, tab):
        """Pressure labels, entries, comboboxes, and buttons"""
        ttk.Label(tab, text="Pressure:").grid(row=0, column=0, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.input_pressure, width=25)
        self.input_pressure_entry.grid(row=0, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.in_pressure_units_cb = ttk.Combobox(tab, textvariable=self.input_pressure_units, values=list(con_pressure.PRESSURE_UNITS), width=25)
        self.in_pressure_units_cb.grid(row=0, column=2, padx=10, pady=(10,0), sticky='nsew')
        ttk.Label(tab, text="to").grid(row=0, column=3, padx=10, pady=(10,0), sticky='nsew')
        self.out_pressure_units_cb = ttk.Combobox(tab, textvariable=self.output_pressure_units, values=list(con_pressure.PRESSURE_UNITS), width=25)
        self.out_pressure_units_cb.grid(row=0, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.input_pressure_entry = ttk.Entry(tab, textvariable=self.output_pressure, width=25)
        self.input_pressure_entry.grid(row=0, column=5, padx=10, pady=(10,0), sticky='nsew')
        pressure_calc_btn = ttk.Button(tab, text="Submit", command=self.calc_pressure)
        pressure_calc_btn.grid(row=0, column=6, padx=10, pady=(10,0), sticky='nsew')

    def _build_length_row(self, tab):
        """Length labels, entries, comboboxes, and buttons"""
        ttk.Label(tab, text="Length:").grid(row=1, column=0, padx=10, pady=(10,0), sticky='nsew')
        self.input_length_entry = ttk.Entry(tab, textvariable=self.input_length, width=25)
        self.input_length_entry.grid(row=1, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.in_length_units_cb = ttk.Combobox(tab, textvariable=self.input_length_units, values=list(con_length.LENGTH_UNITS), width=25)
        self.in_length_units_cb.grid(row=1, column=2, padx=10, pady=(10,0), sticky='nsew')
        ttk.Label(tab, text="to").grid(row=1, column=3, padx=10, pady=(10,0), sticky='nsew')
        self.out_length_units_cb = ttk.Combobox(tab, textvariable=self.output_length_units, values=list(con_length.LENGTH_UNITS), width=25)
        self.out_length_units_cb.grid(row=1, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.input_length_entry = ttk.Entry(tab, textvariable=self.output_length, width=25)
        self.input_length_entry.grid(row=1, column=5, padx=10, pady=(10,0), sticky='nsew')
        length_calc_btn = ttk.Button(tab, text="Submit", command=self.calc_length)
        length_calc_btn.grid(row=1, column=6, padx=10, pady=(10,0), sticky='nsew')

    def _build_weight_row(self, tab):
        """Weight labels, entries, comboboxes, and buttons"""
        ttk.Label(tab, text="Weight:").grid(row=2, column=0, padx=10, pady=(10,0), sticky='nsew')
        self.input_weight_entry = ttk.Entry(tab, textvariable=self.input_weight, width=25)
        self.input_weight_entry.grid(row=2, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.in_weight_units_cb = ttk.Combobox(tab, textvariable=self.input_weight_units, values=list(con_weight.WEIGHT_UNITS), width=25)
        self.in_weight_units_cb.grid(row=2, column=2, padx=10, pady=(10,0), sticky='nsew')
        ttk.Label(tab, text="to").grid(row=2, column=3, padx=10, pady=(10,0), sticky='nsew')
        self.out_weight_units_cb = ttk.Combobox(tab, textvariable=self.output_weight_units, values=list(con_weight.WEIGHT_UNITS), width=25)
        self.out_weight_units_cb.grid(row=2, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.input_weight_entry = ttk.Entry(tab, textvariable=self.output_weight, width=25)
        self.input_weight_entry.grid(row=2, column=5, padx=10, pady=(10,0), sticky='nsew')
        weight_calc_btn = ttk.Button(tab, text="Submit", command=self.calc_weight)
        weight_calc_btn.grid(row=2, column=6, padx=10, pady=(10,0), sticky='nsew')

    def _bind_events(self):
        """Bind all widget traces and <Return> key events."""
        self.output_pressure.trace_add("write", self.update_sci_not)

    def update_sci_not(self, *args):
        """Update output to scientific notation"""
        self.output_pressure.set(f"{float(self.output_pressure.get()):.3e}")
    
    def calc_pressure(self, event=None):
        """Calculate pressure conversions"""
        self.output_pressure.set(con_pressure.convert_pressure(self.input_pressure.get(), self.input_pressure_units.get(), self.output_pressure_units.get()))
        
    def calc_length(self, event=None):
        """Calculate length conversions"""
        self.output_length.set(con_length.convert_length(self.input_length.get(), self.input_length_units.get(), self.output_length_units.get()))
       
    def calc_weight(self, event=None):
        """Calculate weight conversions"""
        self.output_weight.set(con_weight.convert_weight(self.input_weight.get(), self.input_weight_units.get(), self.output_weight_units.get()))
       