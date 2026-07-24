import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np
from Targets import Targets

COMPONENTS = ["TRS Thickness", "Wear Depth", "Wear Percent"]
COMPONENT_LEN = len(COMPONENTS)
DEFAULT_TARGETS = 6
TARGET_MIN = 1
TARGET_MAX = 12
WEAR_DANGER_THRESHOLD = 70 # percent wear above which entry turns danger style
STYLE_PRIMARY = "primary.TEntry"
STYLE_DANGER = "danger.TEntry"

class TargetWear_Panel:
    def __init__(self):
        self.cells          = []
        self.entry_fields   = []
        self.result_entries = []
        self.results        = []
        self.num_targets    = ttk.IntVar(value=DEFAULT_TARGETS)
        self.tab            = None

# ------------------------------------------------------------------ #
#  UI Construction                                                     #
# ------------------------------------------------------------------ #

    def create(self, tab):
        """Build and grid all widgets into the provided tab frame."""
        self.tab = tab
        self._sync_data_to_target_count()
        self._build_header_row(tab)
        self._build_grid(tab)
        self._build_canvas(tab)

    def _build_header_row(self, tab):
        ttk.Label(tab, text="Number of targets").grid(
            row=0, column=2, padx=5, pady=(5,0), sticky='nsew'
        )
        ttk.Scale(
            tab, 
            variable=self.num_targets, 
            from_=1, 
            to=12, 
            orient='horizontal', 
            length=50, 
            command=self.on_command
        ).grid(row=0, column=3, padx=10, pady=(10,0), sticky='nsew')
        
        ttk.Label(tab, textvariable=self.num_targets).grid(
            row=0, column=4, padx=5, pady=(5,0), sticky='nsew'
        )

        for j, name in enumerate(COMPONENTS):
            ttk.Label(tab, text=name).grid(
                row=1, column=j+2, padx=5, pady=(5,0), sticky='nsew'
            )

    def _build_grid(self, tab):
        """Grid target row labels, input cells, result entries, and action buttons."""
        self.entry_fields.clear()
        self.result_entries.clear()

        count = self.num_targets.get()
        for i in range(count):
            ttk.Label(tab, text="TGT " + str(i + 1)).grid(
                row=i+2, column=1, padx=5, pady=(5,0), sticky='nsew'
            )
            result_entry = ttk.Entry(tab, textvariable=self.results[i], state="readonly", style="primary.TEntry")
            result_entry.grid(row=i+2, column=4, padx=5, pady=(5,0), sticky='nsew')
            self.result_entries.append(result_entry)

            row_entries = []
            for j, var in enumerate(self.cells[i]):
                entry = ttk.Entry(tab, textvariable=var)
                entry.bind("<Return>", self.calc_err)
                entry.grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                row_entries.append(entry)
            self.entry_fields.append(row_entries)

        last_row = count + 2
        ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING).grid(
            row=last_row+1, column=4, padx=5, pady=(5,0), sticky='nsew'
        )
        ttk.Button(tab, text="Calculate", command=self.calc_err).grid(
            row=last_row+1, column=3, padx=5, pady=(5,0), sticky='nsew'
        )

    def _build_canvas(self, tab):
        """Embed the Targets canvas widget into the tab."""
        frame = ttk.Frame(tab)
        frame.grid(row=0, column=5, rowspan=15)
        self.targets = Targets(frame, self.num_targets.get())

# ------------------------------------------------------------------ #
#  Data Sync                                                           #
# ------------------------------------------------------------------ #
    def _sync_data_to_target_count(self):
        """Grow or shrink cells/results lists to match the current num_targets value."""
        desired = self.num_targets.get()
        while len(self.cells) < desired:
            self.cells.append([ttk.StringVar(), ttk.StringVar()])
            self.results.append(ttk.DoubleVar(value=0.0))
        while len(self.cells) > desired:
            self.cells.pop()
            self.results.pop()

# ------------------------------------------------------------------ #
#  Calculations                                                        #
# ------------------------------------------------------------------ #

    def calc_err(self, event=None):
        """Calculate wear percent (wear depth / TRS thickness) for each target."""
        values = self._parse_cells()
        wear = self._compute_wear(values)
        for i, pct in enumerate(wear):
            self.results[i].set(0.0 if np.isnan(pct) else round(float(pct), 4))
            style = STYLE_DANGER if pct >= WEAR_DANGER_THRESHOLD else STYLE_PRIMARY
            self.result_entries[i].configure(style=style)
        self.targets.change_color(self.results)

    def _parse_cells(self) -> np.ndarray:
        """Parse cell StringVars into a float array, using NaN for empty/invalid cells."""
        values = np.full((len(self.cells), 2), np.nan)
        for i, row_vars in enumerate(self.cells):
            for j, var in enumerate(row_vars):
                if var is None:
                    continue
                try:
                    values[i, j] = float(var.get())
                except ValueError:
                    var.set("")
        return values

    @staticmethod
    def _compute_wear(values: np.ndarray) -> np.ndarray:
         """Return wear percent as (wear depth / TRS thickness) * 100 for each row."""
         thickness = values[:,0]
         wear_depth = values[:,1]
         with np.errstate(invalid="ignore", divide="ignore"):
             return np.where(thickness != 0, (wear_depth / thickness) * 100, np.nan)

# ------------------------------------------------------------------ #
#  Event Handlers                                                      #
# ------------------------------------------------------------------ #

    def clear(self):
        """Reset all cell inputs, results, and target colors to their defaults."""
        for row_vars in self.cells:
            for var in row_vars:
                if var is not None: 
                    var.set("")
        for i, result in enumerate(self.results):
            result.set(0.0)
            self.result_entries[i].configure(style=STYLE_PRIMARY)
        self.targets.change_color(self.results)

    def update(self, tab):
        """Destroy and rebuild all tab widgets to reflect a changed target count."""
        try:
            int(self.num_targets.get())
            for widget in tab.winfo_children():
                widget.destroy()
            self.entry_fields.clear()
            self.result_entries.clear()
            self.create(tab)
        except (ValueError, ttk.TclError):
            pass

    def on_command(self, *args):
        """Handle slider movement — snap to integer and trigger a panel rebuild."""
        self.num_targets.set(int(float(self.num_targets.get())))
        self.update(self.tab)

