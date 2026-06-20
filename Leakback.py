import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import Constants as c

class Leakback_Panel:
    def __init__(self):
        self.chambersize = {"DLC/SIN": 680, "VEECO C2": 190, "VEECO NEXUS": 170}
        self.pressure_start = ttk.DoubleVar(value="{:.2e}".format(0))
        self.pressure_end = ttk.DoubleVar(value="{:.2e}".format(0))
        self.delta = ttk.DoubleVar(value="{:.2e}".format(0))
        self.ror = ttk.DoubleVar(value="{:.2e}".format(0))
        self.chamber_type = ttk.StringVar(value="DLC/SIN (680 Liters)")
        self.chamber_size = ttk.DoubleVar(value=self.chambersize.get("DLC/SIN"))
        self.checkbox_value = ttk.BooleanVar(value=False)
        self.time = ttk.IntVar(value=15)
        self.fail = ttk.DoubleVar(value="{:.2e}".format(0))

        self.x = np.linspace(0, self.time.get(), self.time.get(), endpoint=True)
        y = self.calc_y()
        self.fail.set("{:.2e}".format(self.calc_fail()))
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.ax.set_title("Leakback", color="#A9BDBD")
        self.ax.tick_params(axis='both', colors="#A9BDBD")
        self.fig.set_facecolor("#002B36")
        self.ax.set_facecolor("#002B36")
        for spine in self.ax.spines.values():
            spine.set_color("#A9BDBD")
        self.ror_line, = self.ax.plot(self.x, y, label=f'ROR', color=c.COLORS["success"])
        self.fail_line = self.ax.axhline(self.fail.get(), label=f'Fail', color=c.COLORS["warning"])
        plt.yscale("log", nonpositive='clip')

        plt.legend(loc='lower right', facecolor=c.COLORS["info"], labelcolor=c.COLORS["inputfg"], edgecolor=c.COLORS["border"], framealpha=0.4)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-120,30),textcoords="offset points", color=c.COLORS["inputfg"],
                    bbox=dict(boxstyle="round", facecolor=c.COLORS["info"], edgecolor=c.COLORS["border"], linewidth=2),
                    arrowprops=dict(arrowstyle="-|>", color=c.COLORS["inputfg"]))
        self.annot.set_visible(False)
        self.annot_fail = self.ax.annotate("", xy=(0,0), xytext=(-120,30),textcoords="offset points", color=c.COLORS["inputfg"],
                    bbox=dict(boxstyle="round", facecolor=c.COLORS["info"], edgecolor=c.COLORS["border"], linewidth=2))
        self.annot.set_visible(False)
        self.update_fail_annot()
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def create(self, tab):
        type_label = ttk.Label(tab, text="Chamber type:")
        type_label.grid(row=0, column=1, padx=10, pady=(10,0), sticky='nsew')
        self.chamber_entry1 = ttk.Combobox(tab, textvariable=self.chamber_type, values=list(f"{t_type} ({size} Liters)" for t_type, size in self.chambersize.items()), width=25)
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
        time_label = ttk.Label(tab, text="Time:")
        time_label.grid(row=1, column=3, pady=(10,0), sticky='nsew')
        time_entry = ttk.Entry(tab, textvariable=self.time)
        time_entry.grid(row=1, column=4, pady=(10,0), sticky='nsew')
        self.time_slider = ttk.Scale(tab, variable=self.time, from_=1, to=30, length=150, orient='horizontal', command=self.on_slider_change)
        self.time_slider.grid(row=2, column=3, columnspan=2, padx=10, pady=(10,0), sticky='new')

        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=5, rowspan=8, padx=10, pady=(20,0), sticky='nsew')

    def update_size(self, event=None):
        if self.checkbox_value.get():
            if self.chamber_type.get().split(" (")[0] in self.chambersize:
                size = int(self.chamber_type.get().split(" (")[1].split(" Liters)")[0])
                self.chamber_size.set(size)
                self.chamber_type.set(size)
            else:
                try:
                    self.chamber_size.set(int(self.chamber_type.get()))
                    self.chamber_type.set(int(self.chamber_type.get()))
                except:
                    self.chamber_size.set(0)
                    self.chamber_type.set(0)
        else:
            if self.chamber_type.get().split(" (")[0] in self.chambersize:
                chamber = self.chamber_type.get().split(" (")
                self.chamber_size.set(self.chambersize.get(chamber[0]))
            elif int(self.chamber_type.get().split(" (")[0]) in self.chambersize.values():
                self.chamber_size.set(self.chamber_type.get().split(" (")[0])
                self.chamber_type.set(f"{next((k for k, v in self.chambersize.items() if v == int(self.chamber_type.get().split(" (")[0])), None)} ({self.chamber_type.get().split(" (")[0]} Liters)")
            else:
                self.chamber_type.set("DLC/SIN (680 Liters)")
                self.chamber_size.set(self.chambersize.get("DLC/SIN"))
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

    def redraw(self):
        y = self.calc_y()
        self.ror_line.set_ydata(y)
        self.fail.set("{:.2e}".format(self.calc_fail()))
        self.fail_line.set_ydata([self.fail.get(), self.fail.get()])
        self.update_fail_annot()
        self.ax.set_ylim([max(self.pressure_start.get(), 1e-6), max(self.fail.get(), self.pressure_end.get()) *2])
        self.canvas.draw()

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
        return self.pressure_start.get() + (self.ror.get() / self.chamber_size.get()) * self.x * 60
    
    def calc_fail(self):
        return max(5e-5/self.chamber_size.get()*self.time.get()*60 + self.pressure_start.get(), 1e-10) 
    
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



