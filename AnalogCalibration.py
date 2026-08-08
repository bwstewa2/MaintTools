import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import Constants as c

### Constants ###
DEFAULT_SETPOINT_LOW = 100
DEFAULT_SETPOINT_HIGH = 1000
DEFAULT_FACTOR = 1.0
DEFAULT_OFFSET = 0.0
MAX_X = 1500
SLIDER_RESOLUTION = 0.000001
FACTOR_MIN, FACTOR_MAX = 0.9, 1.1
OFFSET_MIN, OFFSET_MAX = -0.5, 0.5
LOCK_ICON = "\U0001F512"
UNLOCK_ICON = "\U0001F513"

class AnalogCalibration_Panel:
    """Panel for visualizing and calculating analog calibration adjustments."""

    def __init__(self):
        self._init_vars()
        self._init_plot()

    # ------------------------------------------------------------------ #
    #  Initialization                                                      #
    # ------------------------------------------------------------------ #

    def _init_vars(self):
        """Initialize all tkinter control variables."""
        self.factor          = ttk.StringVar(value=DEFAULT_FACTOR)
        self.offset          = ttk.StringVar(value=DEFAULT_OFFSET)
        self.factor_entry    = ttk.StringVar(value=DEFAULT_FACTOR)
        self.offset_entry    = ttk.StringVar(value=DEFAULT_OFFSET)
        self.percent         = ttk.DoubleVar(value=0.0)
        self.setpoint_low    = ttk.StringVar(value=DEFAULT_SETPOINT_LOW)
        self.setpoint_high   = ttk.StringVar(value=DEFAULT_SETPOINT_HIGH)
        self.setpoint_low_entry  = ttk.StringVar(value=DEFAULT_SETPOINT_LOW)
        self.setpoint_high_entry = ttk.StringVar(value=DEFAULT_SETPOINT_HIGH)
        self.adj_low         = ttk.StringVar(value=DEFAULT_SETPOINT_LOW)
        self.adj_high        = ttk.StringVar(value=DEFAULT_SETPOINT_HIGH)
        self.perc_low        = ttk.StringVar(value=0.00)
        self.perc_high       = ttk.StringVar(value=0.00)
        self.mode            = ttk.StringVar(value="Adjustment")
        self.lock            = ttk.BooleanVar(value=False)
        self.v_low           = None
        self.v_high          = None
        self.base_points     = (200, 1200)

    def _init_plot(self):
        """Initialize the matplotlib figure, lines, and annotations."""
        self.x = np.linspace(0, MAX_X, MAX_X)
        y, _ = self._lin_func()

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self._style_plot()
        self._set_axis_limits()

        self.base_line, = self.ax.plot(self.x, y, label="Base",     color=c.COLORS["warning"])
        self.adj_line,  = self.ax.plot(self.x, y, label="Adjusted", color=c.COLORS["primary"])

        self.ax.legend(
            loc="lower right",
            facecolor=c.COLORS["info"],
            labelcolor=c.COLORS["inputfg"],
            edgecolor=c.COLORS["border"],
            framealpha=0.4,
        )

        self.annot      = self._make_annot(arrow=True)
        self.annot_low  = self._make_annot(arrow=True,  offset=(0, 15))
        self.annot_high = self._make_annot(arrow=True,  offset=(0, 15))
        self.annot.set_visible(False)

        self.calc_deltas()
        self.update_setpoint_annot()

    def _style_plot(self):
        """Apply color theme to the matplotlib axes and figure."""
        self.ax.set_title("Analog Calibration", color=c.COLORS["inputfg"])
        self.ax.tick_params(axis="both", colors=c.COLORS["inputfg"])
        self.fig.set_facecolor(c.COLORS["bg"])
        self.ax.set_facecolor(c.COLORS["bg"])
        for spine in self.ax.spines.values():
            spine.set_color(c.COLORS["inputfg"])

    def _set_axis_limits(self):
        """Set x and y axis limits based on current setpoint and adjusted values."""
        sp_low  = float(self.setpoint_low.get())
        sp_high = float(self.setpoint_high.get())
        adj_low  = float(self.adj_low.get())
        adj_high = float(self.adj_high.get())
        self.ax.set_xlim(sp_low - 100, sp_high + 100)
        self.ax.set_ylim(min(sp_low, adj_low) - 100, max(sp_high, adj_high) + 200)

    def _make_annot(self, arrow: bool = False, offset: tuple = (-120, 30)):
        """Create and return a styled axes annotation."""
        bbox_props = dict(
            boxstyle="round",
            facecolor=c.COLORS["info"],
            edgecolor=c.COLORS["border"],
            linewidth=2,
        )
        kwargs = dict(
            xy=(0, 0),
            xytext=offset,
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
        self._build_mode_row(tab)
        self._build_factor_offset_row(tab)
        self._build_setpoint_row(tab)
        self._build_delta_row(tab)
        self._bind_events(tab)
        self._build_canvas(tab)

    def _build_mode_row(self, tab):
        """Mode label and Adjustment/Correction radio buttons."""
        ttk.Label(tab, text="Mode:").grid(
            row=1, column=1, padx=5, pady=(10, 0), sticky="nse"
        )
        ttk.Radiobutton(
            tab, text="Adjustment", variable=self.mode,
            value="Adjustment", style="Toolbutton", command=self.on_radio_change,
        ).grid(row=1, column=2, padx=(10, 0), pady=(10, 0), sticky="nse")
        ttk.Radiobutton(
            tab, text="Correction", variable=self.mode,
            value="Correction", style="Toolbutton", command=self.on_radio_change,
        ).grid(row=1, column=3, padx=(0, 10), pady=(10, 0), sticky="nse")

    def _build_factor_offset_row(self, tab):
        """Calibration factor and offset sliders, entries, and reset button."""
        ttk.Label(tab, text="Calibration Factor:").grid(
            row=2, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="nse"
        )
        ttk.Scale(
            tab, variable=self.factor, from_=FACTOR_MAX, to=FACTOR_MIN,
            orient="horizontal", length=200, command=self.on_factor_change,
        ).grid(row=2, column=2, columnspan=2, padx=5, pady=(10, 0), sticky="ew")
        self.factor_entry_widget = ttk.Entry(tab, textvariable=self.factor_entry, width=15)
        self.factor_entry_widget.grid(row=2, column=4, padx=10, pady=(10, 0), sticky="nsew")

        ttk.Label(tab, text="Offset (1/1000th):").grid(
            row=2, column=5, padx=5, pady=(10, 0), sticky="nse"
        )
        ttk.Scale(
            tab, variable=self.offset, from_=OFFSET_MIN, to=OFFSET_MAX,
            orient="horizontal", length=200, command=self.on_offset_change,
        ).grid(row=2, column=6, columnspan=2, padx=5, pady=(10, 0), sticky="ew")
        self.offset_entry_widget = ttk.Entry(tab, textvariable=self.offset_entry, width=15)
        self.offset_entry_widget.grid(row=2, column=8, padx=10, pady=(10, 0), sticky="nsew")

        ttk.Button(
            tab, text="Reset", command=self.reset, width=5, bootstyle=WARNING
        ).grid(row=2, rowspan=4, column=10, padx=10, pady=(10, 10), sticky="nsew")

    def _build_setpoint_row(self, tab):
        """Setpoint low/high labels, sliders, and entries."""
        ttk.Label(tab, text="Setpoint Low:").grid(
            row=3, column=0, columnspan=2, padx=5, pady=(10, 0), sticky="nse"
        )
        ttk.Label(tab, text="Setpoint High:").grid(
            row=3, column=5, padx=5, pady=(10, 0), sticky="nse"
        )
        self.sp_low_slider = ttk.Scale(
            tab, variable=self.setpoint_low,
            from_=0, to=int(float(self.setpoint_high.get())) - 1,
            orient="horizontal", length=200, command=self.on_sp_low_change,
        )
        self.sp_low_slider.grid(row=3, column=2, columnspan=2, padx=5, pady=(10, 0), sticky="ew")
        self.sp_low_entry = ttk.Entry(tab, textvariable=self.setpoint_low_entry, width=5)
        self.sp_low_entry.grid(row=3, column=4, padx=10, pady=(10, 0), sticky="nsew")

        self.sp_high_slider = ttk.Scale(
            tab, variable=self.setpoint_high,
            from_=int(float(self.setpoint_low.get())) + 1, to=MAX_X,
            orient="horizontal", length=200, command=self.on_sp_high_change,
        )
        self.sp_high_slider.grid(row=3, column=6, columnspan=2, padx=5, pady=(10, 0), sticky="ew")
        self.sp_high_entry = ttk.Entry(tab, textvariable=self.setpoint_high_entry, width=5)
        self.sp_high_entry.grid(row=3, column=8, padx=10, pady=(10, 0), sticky="nsew")

    def _build_delta_row(self, tab):
        """Percent and adjusted value labels, entries, and lock checkbox."""
        ttk.Label(tab, text="Percent Low:").grid(
            row=4, column=1, padx=5, pady=(10, 10), sticky="nse"
        )
        ttk.Label(tab, text="Percent High:").grid(
            row=4, column=5, padx=5, pady=(10, 10), sticky="nse"
        )
        self.low_adj_label = ttk.Label(tab, text="Adjusted Low:")
        self.low_adj_label.grid(row=4, column=3, padx=5, pady=(10, 10), sticky="nse")
        self.high_adj_label = ttk.Label(tab, text="Adjusted High:")
        self.high_adj_label.grid(row=4, column=7, padx=5, pady=(10, 10), sticky="nse")

        self.entry_perc_low = ttk.Entry(tab, textvariable=self.perc_low, width=5)
        self.entry_perc_low.grid(row=4, column=2, padx=(0, 5), pady=(10, 10), sticky="nsew")
        self.entry_perc_high = ttk.Entry(tab, textvariable=self.perc_high, width=5)
        self.entry_perc_high.grid(row=4, column=6, padx=10, pady=(10, 10), sticky="nsew")
        self.entry_adj_low = ttk.Entry(tab, textvariable=self.adj_low, width=5)
        self.entry_adj_low.grid(row=4, column=4, padx=10, pady=(10, 10), sticky="nsew")
        self.entry_adj_high = ttk.Entry(tab, textvariable=self.adj_high, width=5)
        self.entry_adj_high.grid(row=4, column=8, padx=10, pady=(10, 10), sticky="nsew")

        self.lock_cb = ttk.Checkbutton(
            tab, text=UNLOCK_ICON, variable=self.lock,
            command=self.checkbox_changed, compound="right",
        )
        self.lock_cb.grid(row=4, column=0, padx=(10, 0), pady=(10, 10), sticky="w")

    def _bind_events(self, tab):
        """Bind all widget traces and <Return> key events."""
        self.setpoint_low.trace_add("write",  lambda *a: self.redraw())
        self.setpoint_high.trace_add("write", lambda *a: self.redraw())
        self.offset.trace_add("write",        lambda *a: self.redraw())
        self.factor.trace_add("write",        lambda *a: self.redraw())

        self.sp_low_entry.bind("<Return>",  lambda _: self.on_sp_low_entry())
        self.sp_high_entry.bind("<Return>", lambda _: self.on_sp_high_entry())
        self.offset_entry_widget.bind("<Return>", lambda *a: self.on_offset_entry())
        self.factor_entry_widget.bind("<Return>", lambda *a: self.on_factor_entry())

        self.entry_perc_low.bind("<Return>",  lambda e: self.calc_factor(False))
        self.entry_perc_high.bind("<Return>", lambda e: self.calc_factor(True))
        self.entry_adj_low.bind("<Return>",   lambda e: self.calc_perc(False))
        self.entry_adj_high.bind("<Return>",  lambda e: self.calc_perc(True))

    def _build_canvas(self, tab):
        """Embed the matplotlib figure into the tab."""
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(
            row=0, column=1, columnspan=11, padx=10, pady=(10, 0), sticky="nsew"
        )
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    # ------------------------------------------------------------------ #
    #  Calculations                                                        #
    # ------------------------------------------------------------------ #

    def _lin_func(self) -> tuple[np.ndarray, float]:
        """Return the adjusted y-values and the max y for the current factor/offset."""
        factor = float(self.factor.get())
        offset = float(self.offset.get())
        slope  = 2 - factor
        y      = slope * self.x + offset * 1000
        max_y  = max(slope * MAX_X + offset * 1000, MAX_X)
        return y, max_y

    def calc_deltas(self):
        """Recalculate adjusted low and high values from current factor and offset."""
        try:
            factor = float(self.factor.get())
            offset = float(self.offset.get())
            slope  = 2 - factor
            self.adj_low.set("{:.2f}".format(slope * float(self.setpoint_low.get())  + offset * 1000))
            self.adj_high.set("{:.2f}".format(slope * float(self.setpoint_high.get()) + offset * 1000))
        except (ValueError, ZeroDivisionError):
            pass

    def calc_factor(self, high: bool):
        """Calculate and set factor/offset from a percent error input."""
        c.str_nan_check([
                    (self.perc_high, 0.00),
                    (self.perc_low, 0.00),
                             ])
        sp_l = float(self.setpoint_low.get())
        sp_h = float(self.setpoint_high.get())
        sp   = sp_h if high else sp_l
        perc = float(self.perc_high.get()) if high else float(self.perc_low.get())

        if self.lock.get():
            self.perc_high.set(perc)
            self.adj_high.set(float(self.setpoint_high.get()) * (1 + perc / 100))

        delta = sp * (1 + perc / 100)
        run   = sp_h - sp_l
        rise  = delta - float(self.adj_low.get()) if high else float(self.adj_high.get()) - delta
        slope = rise / run
        self.factor.set("{:.6f}".format(2 - slope))
        self.factor_entry.set(self.factor.get())
        self.offset.set("{:.6f}".format((delta - slope * sp) / 1000))
        self.offset_entry.set(self.offset.get())
        self.redraw()

    def calc_perc(self, high: bool):
        """Calculate percent error from an adjusted value entry, then update factor."""
        c.str_nan_check([
            (self.adj_high, self.setpoint_high.get()),
            (self.adj_low, self.setpoint_low.get()),
                     ])
        sp  = float(self.setpoint_high.get()) if high else float(self.setpoint_low.get())
        adj = float(self.adj_high.get())      if high else float(self.adj_low.get())
        pct = (adj - sp) / sp * 100 if sp != 0 else 0.0
        if high:
            self.perc_high.set(pct)
        else:
            self.perc_low.set(pct)
        self.calc_factor(high)

    # ------------------------------------------------------------------ #
    #  Plot Updates                                                        #
    # ------------------------------------------------------------------ #

    def redraw(self, event=None):
        """Recompute y-data, update axis limits and annotations, then redraw."""
        self.calc_deltas()
        y, _ = self._lin_func()
        self.adj_line.set_ydata(y)
        self._set_axis_limits()
        self._redraw_setpoint_arrows()
        self.sp_low_slider.configure(to=float(self.setpoint_high.get()) - 1)
        self.sp_high_slider.configure(from_=float(self.setpoint_low.get()) + 1)
        self.update_setpoint_annot()
        self.canvas.draw()

    def _redraw_setpoint_arrows(self):
        """Remove and re-draw the vertical delta arrows at each setpoint."""
        if self.v_low:
            self.v_low.remove()
        if self.v_high:
            self.v_high.remove()

        arrow_style = "<-" if self.mode.get() != "Adjustment" else "->"
        arrow_props = dict(arrowstyle=arrow_style, linestyle="--", lw=1.5, color=c.COLORS["info"])

        self.v_low = self.ax.annotate(
            "",
            xy=(float(self.setpoint_low.get()),  float(self.adj_low.get())),
            xytext=(float(self.setpoint_low.get()),  float(self.setpoint_low.get())),
            arrowprops=arrow_props,
        )
        self.v_high = self.ax.annotate(
            "",
            xy=(float(self.setpoint_high.get()), float(self.adj_high.get())),
            xytext=(float(self.setpoint_high.get()), float(self.setpoint_high.get())),
            arrowprops=arrow_props,
        )

    def update_setpoint_annot(self):
        """Update the low and high setpoint annotations with current values."""
        width_px, height_px = self.fig.get_size_inches() * self.fig.dpi

        for annot, sp_var, adj_var, perc_var, x_scale, y_scale in (
            (self.annot_low,  self.setpoint_low,  self.adj_low,  self.perc_low,  1/3, 1/3),
            (self.annot_high, self.setpoint_high, self.adj_high, self.perc_high, 1/6, 1/3),
        ):
            y0 = float(sp_var.get())
            y1 = float(adj_var.get())
            pct = (y1 - y0) * 100 / y0 if y0 != 0 else 0.0
            perc_var.set("{:.2f}".format(pct))
            annot.xy = (y0, y1)
            label = "Adj" if self.mode.get() == "Adjustment" else "Act"
            annot.set_text("Base: {:.2f}\n{}: {:.2f}\n{}%".format(y0, label, y1, perc_var.get()))
            px, py = self.ax.transData.transform((y0, y1))
            annot.set_position((-px * x_scale + width_px / 14, abs(height_px / (5 if x_scale < 0.4 else 10) - py / 3)))
            annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
            annot.get_bbox_patch().set_alpha(0.4)

    def update_annot(self, ind: dict, x: float, y: float):
        """Update the hover annotation to the nearest point on the adjusted line."""
        _, height_px = self.fig.get_size_inches() * self.fig.dpi
        adj_x, adj_y = self.adj_line.get_data()
        _,     base_y = self.base_line.get_data()
        idx = ind["ind"][0]
        x0, y0, y1 = adj_x[idx], adj_y[idx], base_y[idx]
        perc = (y0 - y1) * 400 / y1 if y1 != 0 else 0.0
        self.annot.xy = (x0, y0)
        label = "Adj" if self.mode.get() == "Adjustment" else "Act"
        self.annot.set_text("Base: {:.2f}\n{}: {:.2f}\n{:.2f}%".format(x0, label, y0, perc))
        self.annot.set_position((-x / 3 + 50, abs(height_px / 6 - y / 6)))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        """Show or hide the hover annotation as the cursor moves over the adjusted line."""
        vis = self.annot.get_visible()
        if event.inaxes != self.ax:
            return
        cont, ind = self.adj_line.contains(event)
        if cont:
            self.update_annot(ind, event.x, event.y)
            self.annot.set_visible(True)
            self.fig.canvas.draw_idle()
        elif vis:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    #  Event Handlers                                                      #
    # ------------------------------------------------------------------ #

    def reset(self):
        """Reset factor, offset, and percent fields to defaults and redraw."""
        self.factor.set(DEFAULT_FACTOR)
        self.offset.set(DEFAULT_OFFSET)
        self.factor_entry.set(DEFAULT_FACTOR)
        self.offset_entry.set(DEFAULT_OFFSET)
        self.perc_low.set(0.00)
        self.perc_high.set(0.00)
        self.redraw()

    def on_sp_low_change(self, val):
        """Handle setpoint low slider movement."""
        int_val = int(float(val))
        self.setpoint_low.set(int_val)
        self.setpoint_low_entry.set(int_val)

    def on_sp_high_change(self, val):
        """Handle setpoint high slider movement."""
        int_val = int(float(val))
        self.setpoint_high.set(int_val)
        self.setpoint_high_entry.set(int_val)

    def on_sp_low_entry(self):
        """Validate and apply a manually entered setpoint low value."""
        try:
            val = int(float(self.setpoint_low_entry.get()))
            val = max(0, min(val, int(float(self.setpoint_high.get())) - 1))
            self.on_sp_low_change(val)
        except ValueError:
            self.setpoint_low_entry.set(self.setpoint_low.get())

    def on_sp_high_entry(self):
        """Validate and apply a manually entered setpoint high value."""
        try:
            val = int(float(self.setpoint_high_entry.get()))
            val = max(int(float(self.setpoint_low.get())) + 1, min(val, MAX_X))
            self.on_sp_high_change(val)
        except ValueError:
            self.setpoint_high_entry.set(self.setpoint_high.get())

    def _apply_stepped_value(self, var, entry_var, raw_val: float, fmt: str = "{:.6f}"):
        """Round a slider value to SLIDER_RESOLUTION and apply to both var and entry."""
        stepped = round(raw_val / SLIDER_RESOLUTION) * SLIDER_RESOLUTION
        var.set(fmt.format(stepped))
        entry_var.set(fmt.format(stepped))

    def on_offset_change(self, val):
        """Handle offset slider movement with stepped resolution."""
        self._apply_stepped_value(self.offset, self.offset_entry, float(val))
        self.factor.set("{:.6f}".format(float(self.factor.get())))
        self.factor_entry.set(self.factor.get())

    def on_factor_change(self, val):
        """Handle factor slider movement with stepped resolution."""
        self._apply_stepped_value(self.factor, self.factor_entry, float(val))
        self.offset.set("{:.6f}".format(float(self.offset.get())))
        self.offset_entry.set(self.offset.get())

    def on_offset_entry(self):
        """Validate and apply a manually entered offset value."""
        try:
            val = float(self.offset_entry.get())
            val = max(OFFSET_MIN, min(val, OFFSET_MAX))
            self.on_offset_change(val)
        except ValueError:
            self.offset_entry.set(self.offset.get())

    def on_factor_entry(self):
        """Validate and apply a manually entered factor value."""
        try:
            val = float(self.factor_entry.get())
            val = max(FACTOR_MIN, min(val, FACTOR_MAX))
            self.on_factor_change(val)
        except ValueError:
            self.factor_entry.set(self.factor.get())

    def on_radio_change(self):
        """Swap setpoint and adjusted values when the mode radio button changes."""
        is_adjustment = self.mode.get() == "Adjustment"
        self.low_adj_label.config(text="Adjusted Low:"  if is_adjustment else "Actual Low:")
        self.high_adj_label.config(text="Adjusted High:" if is_adjustment else "Actual High:")
        self.adj_line.set_label("Adjusted" if is_adjustment else "Actual")

        for sp_var, sp_entry_var, adj_var, high in (
            (self.setpoint_low,  self.setpoint_low_entry,  self.adj_low,  False),
            (self.setpoint_high, self.setpoint_high_entry, self.adj_high, True),
        ):
            sp = sp_var.get()
            sp_var.set(adj_var.get())
            sp_entry_var.set(sp_var.get())
            adj_var.set(sp)
            self.calc_perc(high)

    def checkbox_changed(self):
        """Toggle the lock state and enable/disable high adjustment entries."""
        locked = self.lock.get()
        self.lock_cb.configure(text=LOCK_ICON if locked else UNLOCK_ICON)
        state = ["disabled"] if locked else ["!disabled"]
        self.entry_perc_high.state(state)
        self.entry_adj_high.state(state)