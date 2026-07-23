import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import Constants as c

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
    def __init__(self):
        self._init_vars()
        self._init_plot()

    ########################################
    #            INITIALIZATION            #
    ########################################

    def _init_vars(self):
        self.pressure_start = ttk.DoubleVar(value="{:.2e}".format(0))
        self.pressure_end   = ttk.DoubleVar(value="{:.2e}".format(0))
        self.delta          = ttk.DoubleVar(value="{:.2e}".format(0))
        self.ror            = ttk.DoubleVar(value="{:.2e}".format(0))
        self.fail           = ttk.DoubleVar(value="{:.2e}".format(0))
        self.chamber_type   = ttk.StringVar(value=f"{DEFAULT_CHAMBER} ({CHAMBER_SIZES[DEFAULT_CHAMBER]} Liters)")
        self.chamber_size   = ttk.DoubleVar(value=CHAMBER_SIZES.get(DEFAULT_CHAMBER))
        self.checkbox_value = ttk.BooleanVar(value=False)
        self.time           = ttk.IntVar(value=TIME_DEFAULT)

    def _init_plot(self):
        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self.calc_y()

        self.fail.set("{:.2e}".format(self.calc_fail()))

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self._style_plot()
        
        self.ror_line, = self.ax.plot(self.x, y, label=f'ROR', color=c.COLORS["success"])
        self.fail_line = self.ax.axhline(self.fail.get(), label=f'Fail', color=c.COLORS["warning"])

        self.ax.set_yscale("log", nonpositive='clip')
        self.ax.legend(
            loc='lower right', 
            facecolor=c.COLORS["info"], 
            labelcolor=c.COLORS["inputfg"], 
            edgecolor=c.COLORS["border"], 
            framealpha=0.4
        )

        self.annot      = self._make_annot(arrow=True)
        self.annot_fail = self._make_annot(arrow=False)
        self.annot.set_visible(False)
        self.update_fail_annot()

        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def _style_plot(self):
        self.ax.set_title("Leakback", color=PLOT_FG_COLOR)
        self.ax.tick_params(axis="both", colors=PLOT_FG_COLOR)
        self.fig.set_facecolor(PLOT_BG_COLOR)
        self.ax.set_facecolor(PLOT_BG_COLOR)
        for spine in self.ax.spines.values():
            spine.set_color(PLOT_FG_COLOR)

    def _make_annot(self, arrow: bool):
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
    
    ########################################
    #                  UI                  #
    ########################################

    def create(self, tab):
        type_label = ttk.Label(tab, text="Chamber type:")
        type_label.grid(row=0, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.chamber_entry1 = ttk.Combobox(
            tab, textvariable=self.chamber_type, 
            values=list(f"{t_type} ({size} Liters)" for t_type, size in CHAMBER_SIZES.items()), 
            width=25)
        self.chamber_entry1.bind("<<ComboboxSelected>>", self.update_size)
        self.chamber_entry1.grid(row=0, column=2, padx=10, pady=(10,0), sticky='nsew')
        self.chamber_entry2 = ttk.Entry(tab, textvariable=self.chamber_type, width=25)
        self.chamber_entry2.bind("<Return>", self.update_size)
        checkbox = ttk.Checkbutton(tab, text='Manual size entry (L)', variable=self.checkbox_value, command=self.checkbox_changed)
        checkbox.grid(row=0, column=3, columnspan=2, padx=10, pady=(10,0), sticky='nsew')

        start_label = ttk.Label(tab, text="Start Pressure:")
        start_label.grid(row=1, column=1, padx=10, pady=(10,0), sticky='nsew')
        start_entry = ttk.Entry(tab, textvariable=self.pressure_start)
        start_entry.grid(row=1, column=2, padx=10, pady=(10,0), sticky='nsew')
        start_entry.bind("<Return>", self.calc_ror)

        time_label = ttk.Label(tab, text="Time:")
        time_label.grid(row=1, column=3, pady=(10,0), sticky='nsew')
        time_entry = ttk.Entry(tab, textvariable=self.time)
        time_entry.grid(row=1, column=4, pady=(10,0), sticky='nsew')
        self.time_slider = ttk.Scale(tab, variable=self.time, from_=TIME_MIN, to=TIME_MAX, length=150, orient='horizontal', command=self.on_slider_change)
        self.time_slider.grid(row=2, column=3, columnspan=2, padx=10, pady=(10,0), sticky='new')

        end_label = ttk.Label(tab, text="End Pressure:")
        end_label.grid(row=2, column=1, padx=10, pady=(10,0), sticky='nsew')
        end_entry = ttk.Entry(tab, textvariable=self.pressure_end)
        end_entry.grid(row=2, column=2, padx=10, pady=(10,0), sticky='nsew')
        end_entry.bind("<Return>", self.calc_ror)

        delta_label = ttk.Label(tab, text="Pressure Delta:")
        delta_label.grid(row=3, column=1,padx=10, pady=(10,0), sticky='nsew')
        delta_ror = ttk.Entry(tab, state="readonly", textvariable=self.delta)
        delta_ror.grid(row=3, column=2, padx=10, pady=(10,0), sticky='nsew')

        result_label = ttk.Label(tab, text="Rate of Rise:")
        result_label.grid(row=4, column=1, padx=10, pady=(10,0), sticky='nsew')
        result_ror = ttk.Entry(tab, state="readonly", textvariable=self.ror)
        result_ror.grid(row=4, column=2, padx=10, pady=(10,0), sticky='nsew')

        result_label = ttk.Label(tab, text="Fails at:")
        result_label.grid(row=5, column=1, padx=10, pady=(10,0), sticky='nsew')
        result_fail = ttk.Entry(tab, state="readonly", textvariable=self.fail)
        result_fail.grid(row=5, column=2, padx=10, pady=(10,0), sticky='nsew')

        clr_btn = ttk.Button(tab, text="Clear", command=self.clear, bootstyle=WARNING)
        clr_btn.grid(row=6, column=3, columnspan=2, padx=10, pady=(10,10), sticky='nsew')
        btn = ttk.Button(tab, text="Calculate", command=self.calc_ror)
        btn.grid(row=6, column=2, padx=10, pady=(10,10), sticky='nsew')

        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=5, rowspan=8, padx=10, pady=(20,0), sticky='nsew')

    ########################################
    #             CALCULATIONS             #
    ########################################

    def calc_ror(self, event=None):
        try:
            delta_calc = float(self.pressure_end.get()) - float(self.pressure_start.get())
            ror_calc = delta_calc/(self.time.get()*60)*self.chamber_size.get()
            self.delta.set("{:.2e}".format(delta_calc))
            self.ror.set("{:.2e}".format(ror_calc))
        except ValueError:
            self.delta.set("{:.2e}".format(0))
            self.ror.set("{:.2e}".format(0))
        self.redraw()

    def calc_y(self):
        return (self.pressure_start.get() 
                + (self.ror.get() / self.chamber_size.get()) * self.x * 60)
    
    def calc_fail(self):
        return max(FAIL_THRESHOLD/self.chamber_size.get()*self.time.get()*60 
                   + self.pressure_start.get(), PRESSURE_FLOOR) 
    
    ########################################
    #             PLOT UPDATES             #
    ########################################

    def redraw(self):
        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self.calc_y()
        self.ror_line.set_xdata(self.x)
        self.ror_line.set_ydata(y)
        self.fail.set("{:.2e}".format(self.calc_fail()))
        self.fail_line.set_ydata([self.fail.get(), self.fail.get()])
        self.update_fail_annot()
        self.ax.set_ylim([
            max(self.pressure_start.get(), AXIS_MIN), 
            max(self.fail.get(), self.pressure_end.get()) *2
        ])
        self.canvas.draw()

    def update_fail_annot(self):
        y0 = self.fail.get()
        self.annot_fail.xy = (1, y0)
        text = "Fail: {:.2e}".format(y0)
        self.annot_fail.set_text(text)
        self.annot_fail.set_position((-20, 10))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_fail.get_bbox_patch().set_alpha(0.4)

    def update_annot(self, ind):
        ror_x,ror_y = self.ror_line.get_data()
        x0 = ror_x[ind["ind"][0]]
        y0 = ror_y[ind["ind"][0]]
        self.annot.xy = (x0, y0)
        text = "Pressure: {:.2e}\nTime: {:.2f}".format(
            y0,x0
        )
        self.annot.set_text(text)
        self.annot.set_position((100-x0*13.3, -50+min(self.delta.get()/y0, 100)))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.ror_line.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    ########################################
    #            EVENT HANDLERS            #
    ########################################
    
    def update_size(self, event=None):
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
        if self.checkbox_value.get():
            self.chamber_entry1.grid_remove()
            self.chamber_entry2.grid(row=0, column=2, padx=10, pady=(10,0), sticky='nsew')
            self.chamber_entry2.focus_set()
        else:
            self.chamber_entry2.grid_remove()
            self.chamber_entry1.grid(row=0, column=2, padx=10, pady=(20,0), sticky='nsew')
            self.chamber_entry1.focus_set()
        self.update_size()
    
    def clear(self, event=None):
        self.pressure_start.set("{:.2e}".format(0))
        self.pressure_end.set("{:.2e}".format(0))
        self.delta.set("{:.2e}".format(0))
        self.ror.set("{:.2e}".format(0))
        self.fail.set("{:.2e}".format(self.calc_fail()))
        self.redraw()

    def on_slider_change(self, val):
        self.time.set(int(float(val)))
        self.calc_ror()



