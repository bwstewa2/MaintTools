import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import Constants as c

### Constants ###
CHAMBER_SIZES = {"DLC/SIN": 680, "VEECO C2": 190, "VEECO NEXUS": 170}
DEFAULT_CHAMBER = "DLC/SIN"
PLOT_BG_COLOR = "#002B36"
PLOT_FG_COLOR = "#A9BDBD"
FAIL_THRESHOLD = 5e-5
PRESSURE_FLOOR = 1e-10
AXIS_MIN = 1e-6
TIME_DEFAULT = 15
TIME_MIN = 1
TIME_MAX = 30

class Leakback_Panel:
    """Panel for calculating and visualizing vacuum chamber leakback rate of rise."""

    def __init__(self):
        self._init_vars()
        self._init_plot()

    # ------------------------------------------------------------------ #
    #  Initialization                                                      #
    # ------------------------------------------------------------------ #

    def _init_vars(self):
        """Initialize all tkinter control variables."""
        self.pressure_start = ttk.DoubleVar(value="{:.2e}".format(0))
        self.pressure_end   = ttk.DoubleVar(value="{:.2e}".format(0))
        self.delta          = ttk.DoubleVar(value="{:.2e}".format(0))
        self.ror            = ttk.DoubleVar(value="{:.2e}".format(0))
        self.fail           = ttk.DoubleVar(value="{:.2e}".format(0))
        self.chamber_type   = ttk.StringVar(value=f"{DEFAULT_CHAMBER} ({CHAMBER_SIZES[DEFAULT_CHAMBER]} Liters)")
        self.chamber_size   = ttk.DoubleVar(value=CHAMBER_SIZES[DEFAULT_CHAMBER])
        self.checkbox_value = ttk.BooleanVar(value=False)
        self.time           = ttk.IntVar(value=TIME_DEFAULT)

    def _init_plot(self):
        """Initialize the matplotlib figure, lines, annotations, and event hooks."""
        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self._calc_y()

        self.fail.set("{:.2e}".format(self._calc_fail()))

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self._style_plot()

        self.ror_line, = self.ax.plot(self.x, y, label="ROR", color=c.COLORS["success"])
        self.fail_line  = self.ax.axhline(self.fail.get(), label="Fail", color=c.COLORS["warning"])

        self.ax.set_yscale("log", nonpositive="clip")
        self.ax.legend(
            loc="lower right",
            facecolor=c.COLORS["info"],
            labelcolor=c.COLORS["inputfg"],
            edgecolor=c.COLORS["border"],
            framealpha=0.4,
        )

        self.annot      = self._make_annot(arrow=True)
        self.annot_fail = self._make_annot(arrow=False)
        self.annot.set_visible(False)
        self.update_fail_annot()

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def _style_plot(self):
        """Apply color theme to the matplotlib axes and figure."""
        self.ax.set_title("Leakback", color=PLOT_FG_COLOR)
        self.ax.tick_params(axis="both", colors=PLOT_FG_COLOR)
        self.fig.set_facecolor(PLOT_BG_COLOR)
        self.ax.set_facecolor(PLOT_BG_COLOR)
        for spine in self.ax.spines.values():
            spine.set_color(PLOT_FG_COLOR)

    def _make_annot(self, arrow: bool):
        """Create and return a styled axes annotation, with or without an arrow."""
        bbox_props = dict(
            boxstyle="round",
            facecolor=c.COLORS["info"],
            edgecolor=c.COLORS["border"],
            linewidth=2,
        )
        kwargs = dict(
            xy=(0, 0),
            xytext=(-120, 30),
            textcoords="offset points",
            color=c.COLORS["inputfg"],
            bbox=bbox_props,
        )
        if arrow:
            kwargs["arrowprops"] = dict(arrowstyle="-|>", color=c.COLORS["inputfg"])
        return self.ax.annotate("", **kwargs)

    # ------------------------------------------------------------------ #
    #  UI Construction                                                     #
    # ------------------------------------------------------------------ #

    def create(self, tab):
        """Build and grid all widgets into the provided tab frame."""
        self._build_chamber_row(tab)
        self._build_input_rows(tab)
        self._build_output_rows(tab)
        self._build_button_row(tab)
        self._build_time_controls(tab)
        self._build_canvas(tab)

    def _build_chamber_row(self, tab):
        """Chamber type label, combobox, manual entry, and checkbox."""
        ttk.Label(tab, text="Chamber type:").grid(
            row=0, column=1, padx=10, pady=(10, 0), sticky="nsew"
        )

        combo_values = [
            f"{t} ({s} Liters)" for t, s in CHAMBER_SIZES.items()
        ]
        self.chamber_entry1 = ttk.Combobox(
            tab, textvariable=self.chamber_type, values=combo_values, width=25
        )
        self.chamber_entry1.bind("<<ComboboxSelected>>", self.update_size)
        self.chamber_entry1.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")

        self.chamber_entry2 = ttk.Entry(tab, textvariable=self.chamber_type, width=25)
        self.chamber_entry2.bind("<Return>", self.update_size)

        ttk.Checkbutton(
            tab,
            text="Manual size entry (L)",
            variable=self.checkbox_value,
            command=self.checkbox_changed,
        ).grid(row=0, column=3, columnspan=2, padx=10, pady=(10, 0), sticky="nsew")

    def _build_input_rows(self, tab):
        """Start pressure and end pressure input fields."""
        fields = [
            ("Start Pressure:", self.pressure_start, 1),
            ("End Pressure:",   self.pressure_end,   2),
        ]
        for label_text, var, row in fields:
            ttk.Label(tab, text=label_text).grid(
                row=row, column=1, padx=10, pady=(10, 0), sticky="nsew"
            )
            entry = ttk.Entry(tab, textvariable=var)
            entry.grid(row=row, column=2, padx=10, pady=(10, 0), sticky="nsew")
            entry.bind("<Return>", self.calc_ror)

    def _build_output_rows(self, tab):
        """Read-only output fields for delta, ROR, and fail threshold."""
        fields = [
            ("Pressure Delta:", self.delta, 3),
            ("Rate of Rise:",   self.ror,   4),
            ("Fails at:",       self.fail,  5),
        ]
        for label_text, var, row in fields:
            ttk.Label(tab, text=label_text).grid(
                row=row, column=1, padx=10, pady=(10, 0), sticky="nsew"
            )
            ttk.Entry(tab, state="readonly", textvariable=var).grid(
                row=row, column=2, padx=10, pady=(10, 0), sticky="nsew"
            )

    def _build_button_row(self, tab):
        """Calculate and Clear action buttons."""
        ttk.Button(tab, text="Calculate", command=self.calc_ror).grid(
            row=6, column=2, padx=10, pady=(10, 10), sticky="nsew"
        )
        ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING).grid(
            row=6, column=3, columnspan=2, padx=10, pady=(10, 10), sticky="nsew"
        )

    def _build_time_controls(self, tab):
        """Time label, entry, and slider."""
        ttk.Label(tab, text="Time:").grid(
            row=1, column=3, pady=(10, 0), sticky="nsew"
        )
        ttk.Entry(tab, textvariable=self.time).grid(
            row=1, column=4, pady=(10, 0), sticky="nsew"
        )
        self.time_slider = ttk.Scale(
            tab,
            variable=self.time,
            from_=TIME_MIN,
            to=TIME_MAX,
            length=150,
            orient="horizontal",
            command=self.on_slider_change,
        )
        self.time_slider.grid(
            row=2, column=3, columnspan=2, padx=10, pady=(10, 0), sticky="new"
        )

    def _build_canvas(self, tab):
        """Embed the matplotlib figure into the tab."""
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=0, column=5, rowspan=8, padx=10, pady=(20, 0), sticky="nsew"
        )

    # ------------------------------------------------------------------ #
    #  Calculations                                                        #
    # ------------------------------------------------------------------ #

    def _calc_y(self) -> np.ndarray:
        """Return the ROR pressure curve as a numpy array over self.x."""
        return (
            self.pressure_start.get()
            + (self.ror.get() / self.chamber_size.get()) * self.x * 60
        )

    def _calc_fail(self) -> float:
        """Return the pressure value at which the leakback test fails."""
        return max(
            FAIL_THRESHOLD / self.chamber_size.get() * self.time.get() * 60
            + self.pressure_start.get(),
            PRESSURE_FLOOR,
        )

    def calc_ror(self, event=None):
        """Calculate pressure delta and rate of rise, then redraw the plot."""
        try:
            delta_calc = float(self.pressure_end.get()) - float(self.pressure_start.get())
            ror_calc   = delta_calc / (self.time.get() * 60) * self.chamber_size.get()
            self.delta.set("{:.2e}".format(delta_calc))
            self.ror.set("{:.2e}".format(ror_calc))
        except ValueError:
            self.delta.set("{:.2e}".format(0))
            self.ror.set("{:.2e}".format(0))
        self.redraw()

    # ------------------------------------------------------------------ #
    #  Plot Updates                                                        #
    # ------------------------------------------------------------------ #

    def redraw(self):
        """Recompute y-data and refresh the plot."""
        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self._calc_y()
        self.ror_line.set_xdata(self.x)
        self.ror_line.set_ydata(y)
        self.fail.set("{:.2e}".format(self._calc_fail()))
        self.fail_line.set_ydata([self.fail.get(), self.fail.get()])
        self.update_fail_annot()
        self.ax.set_ylim([
            max(self.pressure_start.get(), AXIS_MIN),
            max(self.fail.get(), self.pressure_end.get()) * 2,
        ])
        self.canvas.draw()

    def update_fail_annot(self):
        """Update the fail threshold annotation position and label."""
        y0 = self.fail.get()
        self.annot_fail.xy = (1, y0)
        self.annot_fail.set_text("Fail: {:.2e}".format(y0))
        self.annot_fail.set_position((-20, 10))
        self.annot_fail.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_fail.get_bbox_patch().set_alpha(0.4)

    def update_annot(self, ind: dict):
        """Update the hover annotation to the nearest data point."""
        ror_x, ror_y = self.ror_line.get_data()
        idx = ind["ind"][0]
        x0, y0 = ror_x[idx], ror_y[idx]
        self.annot.xy = (x0, y0)
        self.annot.set_text("Pressure: {:.2e}\nTime: {:.2f}".format(y0, x0))
        self.annot.set_position((100 - x0 * 13.3, -50 + min(self.delta.get() / y0, 100)))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        """Show or hide the hover annotation as the cursor moves over the ROR line."""
        vis = self.annot.get_visible()
        if event.inaxes != self.ax:
            return
        cont, ind = self.ror_line.contains(event)
        if cont:
            self.update_annot(ind)
            self.annot.set_visible(True)
            self.fig.canvas.draw_idle()
        elif vis:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    #  Event Handlers                                                      #
    # ------------------------------------------------------------------ #

    def update_size(self, event=None):
        """Resolve the selected or entered chamber type and update chamber_size."""
        raw = self.chamber_type.get()
        key = raw.split(" (")[0]

        if self.checkbox_value.get():
            # Manual numeric entry mode
            if key in CHAMBER_SIZES:
                size = int(raw.split(" (")[1].split(" Liters)")[0])
            else:
                try:
                    size = int(raw)
                except ValueError:
                    size = 0
            self.chamber_size.set(size)
            self.chamber_type.set(size)
        else:
            # Dropdown selection mode
            if key in CHAMBER_SIZES:
                self.chamber_size.set(CHAMBER_SIZES[key])
            else:
                try:
                    val = int(key)
                except ValueError:
                    val = None
                if val in CHAMBER_SIZES.values():
                    name = next(k for k, v in CHAMBER_SIZES.items() if v == val)
                    self.chamber_size.set(val)
                    self.chamber_type.set(f"{name} ({val} Liters)")
                else:
                    self.chamber_type.set(f"{DEFAULT_CHAMBER} ({CHAMBER_SIZES[DEFAULT_CHAMBER]} Liters)")
                    self.chamber_size.set(CHAMBER_SIZES[DEFAULT_CHAMBER])
        self.calc_ror()

    def checkbox_changed(self):
        """Toggle between the dropdown combobox and the manual text entry."""
        if self.checkbox_value.get():
            self.chamber_entry1.grid_remove()
            self.chamber_entry2.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")
            self.chamber_entry2.focus_set()
        else:
            self.chamber_entry2.grid_remove()
            self.chamber_entry1.grid(row=0, column=2, padx=10, pady=(20, 0), sticky="nsew")
            self.chamber_entry1.focus_set()
        self.update_size()

    def on_slider_change(self, val):
        """Handle time slider movement and trigger recalculation."""
        self.time.set(int(float(val)))
        self.calc_ror()

    def clear(self, event=None):
        """Reset all inputs and outputs to zero and redraw the plot."""
        for var in (self.pressure_start, self.pressure_end, self.delta, self.ror):
            var.set("{:.2e}".format(0))
        self.fail.set("{:.2e}".format(self._calc_fail()))
        self.redraw()