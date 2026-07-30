import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import Delta.DeltaCalculation
import Delta.Wafer
import Delta.History
import Delta.Settings
import Delta.DeltaConstants as dc


# --- Constants ---
WAFER_SIZE_OPTIONS   = ['6"', '8"']
PP_OPTIONS           = [dc.ZERO, dc.NINTY, dc.ONE_EIGHTY, dc.TWO_SEVENTY]
INPUT_ENTRY_WIDTH    = 15
SMALL_ENTRY_WIDTH    = 5
COMBO_SMALL_WIDTH    = 4
DS_SLIDER_MIN        = 0.0
DS_SLIDER_MAX        = 1.5
DS_DEFAULT           = 1.0


class Delta_Panel:
    """Panel for calculating corrected robot station R/T values from eccentricity data."""

    def __init__(self):
        self.history  = Delta.History.History()
        self.settings = Delta.Settings.Settings()
        self.history.read()
        self.settings.read()

        self.delta = Delta.DeltaCalculation.Delta()

        cfg = self.settings.get()
        self.tool          = ttk.Variable()
        self.stn_r         = ttk.IntVar()
        self.stn_t         = ttk.IntVar()
        self.ecc_r         = ttk.IntVar()
        self.ecc_t         = ttk.IntVar()
        self.result_r      = ttk.IntVar()
        self.result_t      = ttk.IntVar()
        self.ws            = ttk.Variable(value=str(cfg["ws"]))
        self.pp            = ttk.Variable(value=str(cfg["pp"]))
        self.ds            = ttk.DoubleVar(value=float(cfg["ds"]))
        self.ia            = ttk.IntVar(value=int(cfg["ia"]))
        self.zoom          = ttk.DoubleVar(value=1.0)
        self.history_index = ttk.IntVar(value=len(self.history.get()))

    # ------------------------------------------------------------------ #
    #  UI Construction                                                     #
    # ------------------------------------------------------------------ #

    def create(self, tab):
        """Build and pack all widgets into the provided tab frame."""
        frame  = ttk.Frame(tab)
        frame1 = ttk.Frame(frame)
        frame2 = ttk.Frame(frame)
        frame3 = ttk.Frame(frame1)
        frame4 = ttk.Frame(frame)
        frame5 = ttk.Frame(frame2)

        frame1.grid(row=0, column=0, pady=(20, 0), padx=5, sticky="nsew")
        frame2.grid(row=1, column=0, pady=(10, 0), padx=5, sticky="nsew")
        frame3.grid(row=9, column=0, columnspan=2,          padx=5, sticky="nsew")
        frame4.grid(row=0, column=5, rowspan=5, pady=(10, 10), padx=5, sticky="nsew")
        frame5.grid(row=0, column=1,                                   sticky="nsew")

        self._build_labels(frame1)
        widgets = self._build_inputs(frame1)
        self._build_controls(frame1, frame3, widgets)
        self._bind_events(widgets)

        self.waf = Delta.Wafer.Wafer(frame4, dc.WAFER_IMAGE_SIZE)
        self.waf.change_position(self.settings.get()["pp"])

        frame.pack(fill="both", expand=True)

    def _build_labels(self, frame):
        """Grid all row labels in the input frame."""
        labels = [
            (0, "Tool:"),
            (1, "Aligner R (10th mil):"),
            (2, "Aligner T (10th deg):"),
            (3, "Station R (micron):"),
            (4, "Station T (1000th deg):"),
            (7, "New Station R Value:"),
            (8, "New Station T Value:"),
        ]
        for row, text in labels:
            ttk.Label(frame, text=text, width=20).grid(
                row=row, column=0, padx=5, pady=(10, 0), sticky="nsew"
            )
        ttk.Label(frame, text="Delta Adjustment (sensitivity):", anchor="center").grid(
            row=5, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="nsew"
        )
        ttk.Label(frame, text="Zoom", anchor="center").grid(
            row=2, column=2, padx=5, pady=(10, 0), sticky="nsew"
        )

    def _build_inputs(self, frame) -> dict:
        """Grid all input widgets and return them keyed by name."""
        tool_entry = ttk.Combobox(
            frame, textvariable=self.tool, width=INPUT_ENTRY_WIDTH,
            values=list({str(t["tool"]) for t in self.history.get() if str(t["tool"]) != ""}),
        )
        tool_entry.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="nsew")

        ws_entry = ttk.Combobox(frame, textvariable=self.ws, values=WAFER_SIZE_OPTIONS, width=COMBO_SMALL_WIDTH)
        ws_entry.grid(row=0, column=2, padx=5, pady=(10, 0), sticky="nsew")

        self.pp_entry = ttk.Combobox(frame, textvariable=self.pp, values=PP_OPTIONS, width=COMBO_SMALL_WIDTH)
        self.pp_entry.grid(row=1, column=2, padx=5, pady=(10, 0), sticky="nsew")

        ecc_r_entry = ttk.Entry(frame, textvariable=self.ecc_r, width=INPUT_ENTRY_WIDTH)
        ecc_r_entry.grid(row=1, column=1, padx=5, pady=(10, 0), sticky="nsew")

        ecc_t_entry = ttk.Entry(frame, textvariable=self.ecc_t, width=INPUT_ENTRY_WIDTH)
        ecc_t_entry.grid(row=2, column=1, padx=5, pady=(10, 0), sticky="nsew")

        stn_r_entry = ttk.Entry(frame, textvariable=self.stn_r, width=INPUT_ENTRY_WIDTH)
        stn_r_entry.grid(row=3, column=1, padx=5, pady=(10, 0), sticky="nsew")

        stn_t_entry = ttk.Entry(frame, textvariable=self.stn_t, width=INPUT_ENTRY_WIDTH)
        stn_t_entry.grid(row=4, column=1, padx=5, pady=(10, 10), sticky="nsew")

        result_r_entry = ttk.Entry(frame, textvariable=self.result_r, state="readonly")
        result_r_entry.grid(row=7, column=1, padx=5, pady=(10, 0), sticky="nsew")

        result_t_entry = ttk.Entry(frame, textvariable=self.result_t, state="readonly")
        result_t_entry.grid(row=8, column=1, padx=5, pady=(10, 0), sticky="nsew")

        ds_entry = ttk.Entry(frame, textvariable=self.ds, width=SMALL_ENTRY_WIDTH)
        ds_entry.grid(row=5, column=2, padx=5, pady=(10, 0), sticky="nsew")

        ds_slider = ttk.Scale(
            frame, variable=self.ds,
            from_=DS_SLIDER_MIN, to=DS_SLIDER_MAX,
            orient="horizontal", length=50,
        )
        ds_slider.grid(row=6, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="ew")

        zoom_slider = ttk.Scale(
            frame, variable=self.zoom,
            from_=dc.ZOOM_MAX, to=dc.ZOOM_MIN,
            orient="vertical", length=50,
        )
        zoom_slider.grid(row=3, column=2, rowspan=2, padx=5, pady=(10, 0), sticky="ns")

        return {
            "ecc_r": ecc_r_entry, "stn_t": stn_t_entry,
            "ws":    ws_entry,    "ds":    ds_entry,
            "ds_slider": ds_slider, "zoom_slider": zoom_slider,
        }

    def _build_controls(self, frame1, frame3, widgets):
        """Grid checkbuttons, action buttons, and navigation buttons."""
        ttk.Checkbutton(
            frame3, text="Aligner Position", variable=self.ia,
            command=self.checkbox_changed, compound="right",
        ).grid(row=0, column=0, padx=5, pady=(10, 0), sticky="w")

        ttk.Button(frame1, text="Reset",      command=self.reset,                   width=5,  bootstyle=WARNING).grid(row=6, column=2, padx=5, pady=(10, 0))
        ttk.Button(frame3, text="Calculate",  command=lambda: self.calculate_enter(None), width=10).grid(row=0, column=1, padx=5, pady=(10, 0))
        ttk.Button(frame3, text="Clear",      command=self.clear,                   width=10, bootstyle=WARNING).grid(row=0, column=2, padx=5, pady=(10, 0))
        ttk.Button(frame1, text="\u2192",     command=self.history_fwd,             width=5,  style=INFO).grid(row=8, column=2, padx=5, pady=(10, 0))
        ttk.Button(frame1, text="\u2190",     command=self.history_back,            width=5,  style=INFO).grid(row=9, column=2, padx=5, pady=(10, 0))
        ttk.Button(frame1, text="\u2934",     command=self.set_results,             width=5,  style=INFO).grid(row=7, column=2, padx=5, pady=(10, 0))

    def _bind_events(self, widgets: dict):
        """Bind all <Return> and selection events to their handlers."""
        widgets["ecc_r"].bind("<Return>",          self.calculate_enter)
        widgets["stn_t"].bind("<Return>",          self.calculate_enter)
        self.pp_entry.bind("<<ComboboxSelected>>", self.update_settings)
        widgets["ws"].bind("<<ComboboxSelected>>", self.update_settings)
        widgets["ds"].bind("<Return>",             self.update_settings)
        widgets["ds_slider"].bind("<ButtonRelease-1>",   self.update_settings)
        widgets["zoom_slider"].bind("<ButtonRelease-1>", self.update_settings)

    # ------------------------------------------------------------------ #
    #  Calculation                                                         #
    # ------------------------------------------------------------------ #

    def calculate(self):
        """Run the delta calculation and update the result and wafer display."""
        try:
            ecc_r = int(self.ecc_r.get())
            ecc_t = int(self.ecc_t.get())
            stn_r = int(self.stn_r.get())
            stn_t = int(self.stn_t.get())
            self.ecc_r.set(ecc_r)
            self.ecc_t.set(ecc_t)
            self.stn_r.set(stn_r)
            self.stn_t.set(stn_t)
            self.delta.calculate_delta(ecc_r, ecc_t, stn_r, stn_t, self.ia.get(), self.ds.get())
            self.result_r.set(self.delta.r)
            self.result_t.set(self.delta.t)
            self.waf.add_delta(self.delta.x, self.delta.y, dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
        except (ValueError, TypeError):
            return

    def calculate_enter(self, event):
        """Calculate and record the result to history."""
        self.calculate()
        self.history.add(
            self.tool.get(), self.ecc_r.get(), self.ecc_t.get(),
            self.stn_r.get(), self.stn_t.get(),
            self.result_r.get(), self.result_t.get(),
            self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get(),
        )
        self.history_index.set(len(self.history.get()) - 1)

    # ------------------------------------------------------------------ #
    #  History Navigation                                                  #
    # ------------------------------------------------------------------ #

    def _load_history_entry(self, index: int):
        """Load a history record by index into all input variables."""
        entry = self.history.get()[index]
        self.tool.set(entry["tool"])
        self.ecc_r.set(entry["ecc_r"])
        self.ecc_t.set(entry["ecc_t"])
        self.stn_r.set(entry["stn_r"])
        self.stn_t.set(entry["stn_t"])
        self.pp.set(entry["pp"])
        self.ws.set(entry["ws"])
        self.ds.set(entry["ds"])
        self.ia.set(entry["ia"])

    def history_fwd(self):
        """Navigate forward through calculation history."""
        max_index = len(self.history.get()) - 1
        if self.history_index.get() < max_index:
            self.history_index.set(self.history_index.get() + 1)
            self._load_history_entry(self.history_index.get())
            self.waf.change_position(self.pp_entry.get())
            self.calculate()
        else:
            self.clear()
            self.history_index.set(min(self.history_index.get() + 1, len(self.history.get())))

    def history_back(self):
        """Navigate backward through calculation history."""
        if self.history_index.get() > 0:
            self.history_index.set(self.history_index.get() - 1)
            try:
                self._load_history_entry(self.history_index.get())
                self.waf.change_position(self.pp_entry.get())
                self.calculate()
            except (IndexError, KeyError):
                self.clear()

    # ------------------------------------------------------------------ #
    #  Event Handlers & Actions                                            #
    # ------------------------------------------------------------------ #

    def reset(self):
        """Reset the delta adjustment to default and recalculate."""
        self.ds.set(DS_DEFAULT)
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        position = self.pp_entry.get() if self._zoom_is_default() else None
        self.waf.change_position(position)
        self.calculate()

    def clear(self):
        """Reset all inputs, results, and the wafer display to zero."""
        for var in (self.tool, self.stn_r, self.stn_t, self.ecc_r, self.ecc_t, self.result_r, self.result_t):
            var.set(0)
        self.waf.remove_delta()

    def set_results(self):
        """Promote the calculated R/T results into the station input fields."""
        self.stn_r.set(self.result_r.get())
        self.stn_t.set(self.result_t.get())
        self.result_r.set(0)
        self.result_t.set(0)

    def checkbox_changed(self):
        """Handle aligner position checkbox toggle."""
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        self.calculate()

    def update_settings(self, event=None):
        """Persist current settings and refresh the wafer position display."""
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        position = self.pp_entry.get() if self._zoom_is_default() else None
        self.waf.change_position(position)
        self.calculate()

    def on_closing(self):
        """Persist history and settings when the application closes."""
        self.history.write()
        self.settings.write()

    # ------------------------------------------------------------------ #
    #  Private Utilities                                                   #
    # ------------------------------------------------------------------ #

    def _zoom_is_default(self) -> bool:
        """Return True if the zoom level has not been changed from 1.0."""
        wafer_size = dc.WAFER_SIZE[self.ws.get()]
        return wafer_size / self.zoom.get() == wafer_size