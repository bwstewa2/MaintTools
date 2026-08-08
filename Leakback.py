import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import Constants as c

### Constants ###
CHAMBER_SIZES = {"DLC/SIN": 680, "VEECO C2": 190, "VEECO NEXUS": 170}
DEFAULT_CHAMBER = "DLC/SIN"
FAIL_THRESHOLD = 5e-5
PRESSURE_FLOOR = 1e-10
AXIS_MIN = 1e-6
DEFAULT_TIME = 15
TIME_MIN = 1
TIME_MAX = 30
DEFAULT_DOUBLE = "{:.2e}".format(0)

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
        self.pressure_start = ttk.DoubleVar(value=DEFAULT_DOUBLE)
        self.pressure_end   = ttk.DoubleVar(value=DEFAULT_DOUBLE)
        self.delta          = ttk.DoubleVar(value=DEFAULT_DOUBLE)
        self.ror            = ttk.DoubleVar(value=DEFAULT_DOUBLE)
        self.fail           = ttk.DoubleVar(value=DEFAULT_DOUBLE)
        self.fail_threshold = ttk.DoubleVar(value=FAIL_THRESHOLD)
        self.chamber_type   = ttk.StringVar(value=f"{DEFAULT_CHAMBER} ({CHAMBER_SIZES[DEFAULT_CHAMBER]} Liters)")
        self.chamber_size   = ttk.DoubleVar(value=CHAMBER_SIZES[DEFAULT_CHAMBER])
        self.checkbox_value = ttk.BooleanVar(value=False)
        self.time           = ttk.IntVar(value=DEFAULT_TIME)

    def _init_plot(self):
        """Initialize the matplotlib figure, lines, annotations, and event hooks."""
        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self._calc_y()

        self.fail.set("{:.2e}".format(self._calc_fail()))

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self._style_plot()
        self._style_ticks()

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
        self.ax.callbacks.connect("ylim_changed", lambda ax: self._style_ticks())

    def _style_plot(self):
        """Apply color theme to the matplotlib axes and figure."""
        self.ax.set_title("Leakback", color=c.COLORS["light"])
        self.fig.set_facecolor(c.COLORS["bg"])
        self.ax.set_facecolor(c.COLORS["bg"])
        for spine in self.ax.spines.values():
            spine.set_color(c.COLORS["light"])

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

    def _style_ticks(self):
        """Re-apply tick label colors after matplotlib regenerates them on ylim change."""
        for label in self.ax.get_xticklabels() + self.ax.get_yticklabels():
            label.set_color(c.COLORS["light"])
        self.ax.tick_params(axis="both", which="major", colors=c.COLORS["light"])
        self.ax.tick_params(axis="both", which="minor", colors=c.COLORS["secondary"])

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
            ("Fail Threshold:", self.fail_threshold, 1),
            ("Start Pressure:", self.pressure_start, 2),
            ("End Pressure:",   self.pressure_end,   3),
        ]
        for label_text, var, row in fields:
            ttk.Label(tab, text=label_text).grid(
                row=row, column=1, padx=10, pady=(10, 0), sticky="nsew"
            )
            entry = ttk.Entry(tab, textvariable=var)
            entry.grid(row=row, column=2, padx=10, pady=(10, 0), sticky="nsew")
            entry.bind("<Return>", self.calc_ror)

    def _build_output_rows(self, tab):
        """Read-only output fields for delta, fail threshold, and ROR."""
        fields = [
            ("Pressure Delta:", self.delta, 4, None, None),
            ("Fails at:",       self.fail,  5, None, None),
            ("Rate of Rise:",   self.ror,   6, "ror_entry", c.STYLE_PRIMARY),
        ]
        for label_text, var, row, attr, style in fields:
            ttk.Label(tab, text=label_text).grid(
                row=row, column=1, padx=10, pady=(10, 0), sticky="nsew"
            )
            entry = ttk.Entry(tab, state="readonly", textvariable=var)
            entry.grid(row=row, column=2, padx=10, pady=(10, 0), sticky="nsew")
            if attr:
                setattr(self, attr, entry)
            if style: 
                entry.configure(style=style)

    def _build_button_row(self, tab):
        """Calculate and Clear action buttons."""
        ttk.Button(tab, text="Calculate", command=self.calc_ror).grid(
            row=7, column=2, padx=10, pady=(10, 10), sticky="nsew"
        )
        ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING).grid(
            row=7, column=3, columnspan=2, padx=10, pady=(10, 10), sticky="nsew"
        )

    def _build_time_controls(self, tab):
        """Time label, entry, and slider."""
        ttk.Label(tab, text="Minutes:").grid(
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
            float(self.pressure_start.get())
            + (self.ror.get() / self.chamber_size.get()) * self.x * 60
        )

    def _calc_fail(self) -> float:
        """Return the pressure value at which the leakback test fails."""
        return max(
            float(self.fail_threshold.get()) / self.chamber_size.get() * self.time.get() * 60
            + float(self.pressure_start.get()),
            PRESSURE_FLOOR,
        )


    def calc_ror(self, event=None):
        """Calculate pressure delta and rate of rise, then redraw the plot."""
        c.nan_check([
                    (self.fail_threshold, FAIL_THRESHOLD),
                    (self.pressure_start,  DEFAULT_DOUBLE),
                    (self.pressure_end,    DEFAULT_DOUBLE),
                    (self.time,            DEFAULT_TIME),
                ])
        delta_calc = float(self.pressure_end.get()) - float(self.pressure_start.get())
        ror_calc   = delta_calc / (self.time.get() * 60) * self.chamber_size.get()
        self.delta.set("{:.2e}".format(delta_calc))
        self.ror.set("{:.2e}".format(ror_calc))
        if self.ror.get() > self.fail.get():
            self.ror_entry.configure(style=c.STYLE_DANGER)
        else:
            self.ror_entry.configure(style=c.STYLE_PRIMARY)
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
        self.fig.tight_layout()
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
        raw = self.chamber_type.get()
        name_part = raw.split(" (")[0]

        if self.checkbox_value.get():
            # Manual entry mode — user typed a raw number or a full display string
            if name_part in CHAMBER_SIZES:
                # Display string left over; extract its numeric size
                try:
                    size = int(raw.split(" (")[1].split(" Liters)")[0])
                except (IndexError, ValueError):
                    size = 0
            else:
                try:
                    size = int(name_part)
                except ValueError:
                    size = 0
            self.chamber_size.set(size)
            self.chamber_type.set(size)

        else:
            # Combobox mode — expect "NAME (SIZE Liters)" or a leftover plain number
            if name_part in CHAMBER_SIZES:
                self.chamber_size.set(CHAMBER_SIZES[name_part])
            else:
                # Handle a plain number left over from manual-entry mode
                try:
                    numeric = int(name_part)
                except ValueError:
                    numeric = None

                matched_key = next(
                    (k for k, v in CHAMBER_SIZES.items() if v == numeric), None
                )
                if matched_key is not None:
                    self.chamber_size.set(numeric)
                    self.chamber_type.set(f"{matched_key} ({numeric} Liters)")
                else:
                    default_key = DEFAULT_CHAMBER
                    self.chamber_type.set(
                        f"{default_key} ({CHAMBER_SIZES[default_key]} Liters)"
                    )
                    self.chamber_size.set(CHAMBER_SIZES[default_key])

        self.calc_ror()

    def checkbox_changed(self):
        if self.checkbox_value.get():
            self.chamber_entry1.grid_remove()
            self.chamber_entry2.grid(row=0, column=2, padx=10, pady=(10, 0), sticky='nsew')
            # Clear the field so the user starts fresh with a plain number
            self.chamber_type.set("")
            self.chamber_entry2.focus_set()
        else:
            self.chamber_entry2.grid_remove()
            self.chamber_entry1.grid(row=0, column=2, padx=10, pady=(20, 0), sticky='nsew')
            self.chamber_entry1.focus_set()
            # Restore a valid display string when returning to combobox mode
            self.update_size()

    def on_slider_change(self, val):
        """Handle time slider movement and trigger recalculation."""
        self.time.set(int(float(val)))
        self.calc_ror()

    def clear(self, event=None):
        """Reset all inputs and outputs to zero and redraw the plot."""
        for var in (self.pressure_start, self.pressure_end, self.delta, self.ror):
            var.set(DEFAULT_DOUBLE)
        self.fail.set("{:.2e}".format(self._calc_fail()))
        self.redraw()
