import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import numpy as np

### Constants ###
PARAMETERS = ["BV", "BI", "SV", "SC", "RF", "PBN BI"]
COMPONENTS = ["PROG", "PS", "RB", "MAX ERROR"]
NUM_PARAMS = len(PARAMETERS)
NUM_COLS = 3 # PROG, PS, RB — the three editable measurement columns

class Parameter_Panel:
    """Panel for measuring and calculating max percentage error across parameters."""

    def __init__(self):
        self._init_vars()

# ------------------------------------------------------------------ #
#  Initialization                                                      #
# ------------------------------------------------------------------ #

    def _init_vars(self):
        """Initialize cell input variables and result variables.

        The cell grid is NUM_PARAMS x NUM_COLS. Rows 3–5 (BF, SC, RF, PBN BI)
        have no PROG column, represented by None in column 0.
        """
        self.cells = [
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [ttk.StringVar(value=""), ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None,                    ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None,                    ttk.StringVar(value=""), ttk.StringVar(value="")],
            [None,                    ttk.StringVar(value=""), ttk.StringVar(value="")]
        ]
        self.results = [ttk.DoubleVar(value=0) for _ in range(NUM_PARAMS)]
        self.entry_fields = []
        self.result_entries = []

# ------------------------------------------------------------------ #
#  UI Construction                                                     #
# ------------------------------------------------------------------ #

    def create(self, tab):
        """Build and grid all widgets into the provided tab frame."""
        self._build_header_labels(tab)
        self._build_result_entries(tab)
        self._build_cell_entries(tab)
        self._build_buttons(tab)

    def _build_header_labels(self, tab):
        """Grid parameter row labels and component column headers."""
        for i, name in enumerate(PARAMETERS):
            ttk.Label(tab, text=name+":").grid(
                row=i+2, column=1, padx=5, pady=(5,0), sticky='nsew'
            )
    
        for i, name in enumerate(COMPONENTS):
            ttk.Label(tab, text=name).grid(
                row=1, column=i+2, padx=5, pady=(5,0), sticky='nsew'
            )

    def _build_result_entries(self, tab):
        """Grid the read-only result entries in the MAX ERROR column."""
        for i, var in enumerate(self.results):
            entry = ttk.Entry(tab, textvariable=var, state="readonly")
            entry.grid(row=i+2, column=5, padx=5, pady=(5,0), sticky='nsew')
            self.result_entries.append(entry)

    def _build_cell_entries(self, tab):
        """Grid editable and read-only cell entries for the measurement grid."""
        for i, row_vars in enumerate(self.cells):
            row_entries = []
            for j, var in enumerate(row_vars):
                if var is not None:
                    entry = ttk.Entry(tab, textvariable=var)
                    entry.bind("<Return>", self._calc_err)
                    entry.grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                else:
                    entry = ttk.Entry(tab, textvariable=var, state="readonly")
                    entry.grid(row=i+2, column=j+2, padx=5, pady=(5,0), sticky='nsew')
                row_entries.append(entry)
            self.entry_fields.append(row_entries)

    def _build_buttons(self, tab):
        """Grid the Calculate and Clear action buttons."""
        clr_btn = ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING)
        clr_btn.grid(row=8, column=5, padx=10, pady=(20,20), sticky='nsew')
        sbmt_btn = ttk.Button(tab, text="Calculate", command=self._calc_err)
        sbmt_btn.grid(row=8, column=4, padx=10, pady=(20,20), sticky='nsew')

# ------------------------------------------------------------------ #
#  Calculations                                                        #
# ------------------------------------------------------------------ #

    def _calc_err(self, event=None):
        """Calculate the max percentage error across each parameter row."""
        values = self._parse_cells()
        error = self._compute_error(values)
        for i, val in enumerate(error):
            self.results[i].set(0.0 if np.isnan(val) else round(val, 6))

    def _parse_cells(self):
        """Parse cell StringVars into a float array, using NaN for empty/invalid cells."""
        values = np.full((NUM_PARAMS, NUM_COLS), np.nan)
        for i, row_vars in enumerate(self.cells):
            for j, var in enumerate(row_vars):
                if var is None:
                    continue
                try:
                    values[i, j] = float(var.get())
                except ValueError:
                    self.cells[i][j].set("")
        return values

    @staticmethod
    def _compute_error(values: np.ndarray) -> np.ndarray:
        """Return the row-wise max percentage error from a 2D float array.

        Rows where all values are NaN produce a 0.0 error (no warning).
        """
        error = np.zeros(values.shape[0])
        for i, row in enumerate(values):
            valid = row[~np.isnan(row)]
            if len(valid) < 2:
                continue  # need at least 2 values to compute an error
            max_p  = valid.max()
            spread = (max_p - valid.min()) * 100
            if max_p != 0 and spread != 0:
                error[i] = spread / max_p
        return error

# ------------------------------------------------------------------ #
#  Event Handlers                                                      #
# ------------------------------------------------------------------ #

    def clear(self):
        """Reset all cell inputs and results to their default empty/zero state."""
        for i in range(len(self.cells)):
            for j in range(len(self.cells[i])):
                if self.cells[i][j]: 
                    self.cells[i][j].set("")
        for i in range(len(self.results)):
            self.results[i].set(0)