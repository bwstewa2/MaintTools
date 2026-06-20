import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np
from Targets import Targets

class TargetWear_Panel:
    def __init__(self):
        self.cells = []
        self.entry_fields = []
        self.result_entries = []
        self.results = []
        self.num_targets = ttk.IntVar(value=6)
        self.components = ["TRS Thickness", "Wear Depth", "Wear Percent"]

    def create(self, tab):
        self.tab = tab
        last_row = 0
        ttk.Label(tab, text="Number of targets").grid(row=0, column=2, padx=5, pady=(5,0), sticky='nsew')
        self.num_label = ttk.Label(tab, textvariable=self.num_targets)
        self.num_label.grid(row=0, column=4, padx=5, pady=(5,0), sticky='nsew')
        ttk.Scale(tab, variable=self.num_targets, from_=1, to=12, orient='horizontal', length=50, command=self.on_command).grid(row=0, column=3, padx=10, pady=(10,0), sticky='nsew')

        while len(self.cells) < self.num_targets.get():
            self.cells.append([ttk.StringVar(value=""),ttk.StringVar(value="")])
            self.results.append(ttk.DoubleVar(value=0))

        while len(self.cells) > self.num_targets.get():
            self.cells.pop()
            self.results.pop()

        for i in range(self.num_targets.get()):
            ttk.Label(tab, text="TGT " + str(i + 1)).grid(row=i+2, column=1, padx=5, pady=(5,0), sticky='nsew')
    
        for i in range(len(self.components)):
            ttk.Label(tab, text=self.components[i]).grid(row=1, column=i+2, padx=5, pady=(5,0), sticky='nsew')
        
        for i in range(len(self.cells)):
            entry_fields = []
            entry = ttk.Entry(tab, textvariable=self.results[i], state="readonly", style="primary.TEntry")
            entry.grid(row=i+2, column=4, padx=5, pady=(5,0), sticky='nsew')
            self.result_entries.append(entry)
            for j in range(len(self.cells[i])):
                if self.cells[i][j]:
                    entry_t = ttk.Entry(tab, textvariable=self.cells[i][j])
                    entry_t.bind("<Return>", self.calc_err)
                    entry_t.grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                else:
                    entry_t = ttk.Entry(tab, textvariable=self.cells[i][j], state="readonly").grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                entry_fields.append(entry_t)
            self.entry_fields.append(entry_fields)
            last_row = i + 2

        clr_btn = ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING)
        clr_btn.grid(row=last_row+1, column=4, padx=5, pady=(5,0), sticky='nsew')
        sbmt_btn = ttk.Button(tab, text="Calculate", command=self.calc_err)
        sbmt_btn.grid(row=last_row+1, column=3, padx=5, pady=(5,0), sticky='nsew')

        frame = ttk.Frame(tab)
        frame.grid(row=0, column=5, rowspan=15)
        self.targets = Targets(frame, self.num_targets.get())

    def clear(self):
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                if self.cells[i][j]: 
                    self.cells[i][j].set("")
        for i in range(len(self.results)):
            self.results[i].set(0)
            self.result_entries[i].configure(style="primary.TEntry")
        self.targets.change_color(self.results)
            
    def calc_err(self, event=None):
        cells = [[None] * len(sublist) for sublist in self.cells]
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                if self.cells[i][j]:
                    try:
                        cells[i][j] = float(self.cells[i][j].get())
                    except:
                        cells[i][j] = np.nan
                        self.cells[i][j].set("")
                else: 
                    cells[i][j] = np.nan
        cells = np.array(cells)
        error = (cells[:,1] / cells[:,0])*100
        for i in range(len(error)):
            self.results[i].set(0 if np.isnan(error[i]) else error[i])
            if error[i] >= 70:
                self.result_entries[i].configure(style="danger.TEntry")
            else:
                self.result_entries[i].configure(style="primary.TEntry")
        self.targets.change_color(self.results)

    def update(self, tab):
        try:
            int(self.num_targets.get())
            for widget in tab.winfo_children():
                widget.destroy()
            self.create(tab)
        except:
            pass

    def on_command(self, *args):
        self.num_targets.set(int(float(self.num_targets.get())))
        self.update(self.tab)

