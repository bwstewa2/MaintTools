import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np


class Parameter_Panel:
    def __init__(self):
        self.cells = [
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None, ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None, ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None, ttk.StringVar(value=""), ttk.StringVar(value="")]
        ]
        self.entry_fields = []
        self.result_entries = []
        self.results = [ttk.DoubleVar(value=0), ttk.DoubleVar(value=0), ttk.DoubleVar(value=0), ttk.DoubleVar(value=0), ttk.DoubleVar(value=0), ttk.DoubleVar(value=0)]
        self.parameters = ["BV", "BI", "SV", "SC", "RF", "PBN BI"]
        self.components = ["PROG", "PS", "RB", "MAX ERROR"]

    def create(self, tab):
        def calc_err(event=None):
            cells = [[None] * len(sublist) for sublist in self.cells]
            for i in range(len(self.cells)):
                for j in range(len(self.cells[i])):
                    if self.cells[i][j]:
                        try:
                            print(self.cells[i][j].get())
                            cells[i][j] = float(self.cells[i][j].get())
                        except:
                            cells[i][j] = np.nan
                            self.cells[i][j].set("")
                    else: 
                        cells[i][j] = np.nan
            cells = np.array(cells)

            max_p = np.nanmax(cells, axis=1)
            min_p = np.nanmin(cells, axis=1)

            error = (max_p - min_p)*100
            error = np.divide(error, max_p, where=error!=0)

            for i in range(len(error)):
                self.results[i].set(0 if np.isnan(error[i]) else error[i])

        for i in range(len(self.parameters)):
            ttk.Label(tab, text=self.parameters[i]).grid(row=i+2, column=1, padx=5, pady=(5,0), sticky='nsew')
    
        for i in range(len(self.components)):
            ttk.Label(tab, text=self.components[i]).grid(row=1, column=i+2, padx=5, pady=(5,0), sticky='nsew')

        for i in range(len(self.results)):
            self.result_entries.append(ttk.Entry(tab, textvariable=self.results[i], state="readonly").grid(row=i+2, column=5, padx=5, pady=(5,0), sticky='nsew'))

        for i in range(len(self.cells)):
            entry_fields = []
            for j in range(len(self.cells[i])):
                if self.cells[i][j]:
                    entry_t = ttk.Entry(tab, textvariable=self.cells[i][j])
                    entry_t.bind("<Return>", calc_err)
                    entry_t.grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                else:
                    entry_t = ttk.Entry(tab, textvariable=self.cells[i][j], state="readonly").grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                entry_fields.append(entry_t)
            self.entry_fields.append(entry_fields)

        clr_btn = ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING)
        clr_btn.grid(row=8, column=5, padx=10, pady=(20,20), sticky='nsew')
        sbmt_btn = ttk.Button(tab, text="Calculate", command=calc_err)
        sbmt_btn.grid(row=8, column=4, padx=10, pady=(20,20), sticky='nsew')

    def clear(self):
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                if self.cells[i][j]: 
                    self.cells[i][j].set("")
        for i in range(len(self.results)):
            self.results[i].set(0)