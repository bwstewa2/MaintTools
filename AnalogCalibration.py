import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import Constants as c

class AnalogCalibration_Panel:
    def __init__(self):
        self.factor = ttk.StringVar(value=1.0)
        self.offset = ttk.StringVar(value=0.0)
        self.percent = ttk.DoubleVar(value=0.0)
        self.base_points = (200, 1200)
        self.max_x = 1500
        self.setpoint_low = ttk.StringVar(value=100)
        self.setpoint_high = ttk.StringVar(value=1000)
        self.delta_low = ttk.StringVar()
        self.delta_high = ttk.StringVar()
        self.v_low = None
        self.v_high = None
        self.perc_low = ttk.StringVar(value=0.00)
        self.perc_high = ttk.StringVar(value=0.00)

        self.x = np.linspace(0, self.max_x, self.max_x)
        y, max_y = self.lin_func()
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.ax.set_xlim(float(self.setpoint_low.get()) - 100, float(self.setpoint_high.get()) + 100)
        self.ax.set_ylim([0, max_y + 100])
        self.base_line, = self.ax.plot(self.x, y, label=f'Base', color=c.COLORS["warning"])
        self.adj_line, = self.ax.plot(self.x, y, label=f'Adjustment', color=c.COLORS["primary"])
        self.ax.set_title("Analog Calibration", color=c.COLORS["inputfg"])
        self.ax.tick_params(axis='both', colors=c.COLORS["inputfg"])
        self.fig.set_facecolor(c.COLORS["bg"])
        self.ax.set_facecolor(c.COLORS["bg"])
        for spine in self.ax.spines.values():
            spine.set_color(c.COLORS["inputfg"])

        plt.legend(loc='lower right', facecolor=c.COLORS["info"], labelcolor=c.COLORS["inputfg"], edgecolor=c.COLORS["border"], framealpha=0.4)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-120,30),textcoords="offset points", color=c.COLORS["inputfg"],
                    bbox=dict(boxstyle="round", facecolor=c.COLORS["info"], edgecolor=c.COLORS["border"], linewidth=2),
                    arrowprops=dict(arrowstyle="-|>", color=c.COLORS["inputfg"]))
        self.annot.set_visible(False)
        self.annot_low = self.ax.annotate("", xy=(0,0), xytext=(0,15), textcoords="offset points", color=c.COLORS["inputfg"],
                    bbox=dict(boxstyle="round", facecolor=c.COLORS["info"], edgecolor=c.COLORS["border"], linewidth=2),
                    arrowprops=dict(arrowstyle="-|>", color=c.COLORS["inputfg"]))
        self.annot_high = self.ax.annotate("", xy=(0,0), xytext=(0,15), textcoords="offset points", color=c.COLORS["inputfg"],
                    bbox=dict(boxstyle="round", facecolor=c.COLORS["info"], edgecolor=c.COLORS["border"], linewidth=2),
                    arrowprops=dict(arrowstyle="-|>", color=c.COLORS["inputfg"]))
        
        self.calc_deltas()
        self.update_setpoint_annot()

    def create(self, tab):
        factor_label = ttk.Label(tab, text="Calibration Factor:")
        factor_label.grid(row=1, column=1, padx=5, pady=(10,0), sticky='nse')
        offset_label = ttk.Label(tab, text="Offset:")
        offset_label.grid(row=1, column=5, padx=5, pady=(10,0), sticky='nse')
        factor_slider = ttk.Scale(tab, variable=self.factor, from_=2, to=0.1, orient='horizontal', length=100, command=self.on_factor_change)
        factor_slider.grid(row=1, column=2, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        offset_slider = ttk.Scale(tab, variable=self.offset, from_=-0.5, to=0.5, orient='horizontal', length=100, command=self.on_offset_change)
        offset_slider.grid(row=1, column=6, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        setpoint_low_label = ttk.Label(tab, text="Setpoint Low:")
        setpoint_low_label.grid(row=3, column=1, padx=5, pady=(10,0), sticky='nse')
        setpoint_high_label = ttk.Label(tab, text="Setpoint High:")
        setpoint_high_label.grid(row=3, column=5, padx=5, pady=(10,0), sticky='nse')
        self.sp_low_slider = ttk.Scale(tab, variable=self.setpoint_low, from_=0, to=self.setpoint_high.get(), orient='horizontal', length=50, command=self.on_sp_low_change)
        self.sp_low_slider.grid(row=3, column=2, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        self.sp_high_slider = ttk.Scale(tab, variable=self.setpoint_high, from_=self.setpoint_low.get(), to=self.max_x, orient='horizontal', length=50, command=self.on_sp_high_change)
        self.sp_high_slider.grid(row=3, column=6, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        low_factor_label = ttk.Label(tab, text="Percent Low:")
        low_factor_label.grid(row=4, column=1, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        high_factor_label = ttk.Label(tab, text="Percent High:")
        high_factor_label.grid(row=4, column=5, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        low_adj_label = ttk.Label(tab, text="Adjustment Low:")
        low_adj_label.grid(row=4, column=3, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        high_adj_label = ttk.Label(tab, text="Adjustment High:")
        high_adj_label.grid(row=4, column=7, columnspan=1, padx=5, pady=(10,10), sticky='nse')

        ttk.Entry(tab, textvariable=self.factor, width=15).grid(row=1, column=4, padx=10, pady=(10,0), sticky='nsew')
        ttk.Entry(tab, textvariable=self.offset, width=15).grid(row=1, column=8, padx=10, pady=(10,0), sticky='nsew')
        ttk.Entry(tab, textvariable=self.setpoint_low, width=5).grid(row=3, column=4, padx=10, pady=(10,0), sticky='nsew')
        ttk.Entry(tab, textvariable=self.setpoint_high, width=5).grid(row=3, column=8, padx=10, pady=(10,0), sticky='nsew')
        entry_adj_low = ttk.Entry(tab, textvariable=self.delta_low, width=5)
        entry_adj_low.grid(row=4, column=4, padx=10, pady=(10,10), sticky='nsew')
        entry_adj_high = ttk.Entry(tab, textvariable=self.delta_high, width=5)
        entry_adj_high.grid(row=4, column=8, padx=10, pady=(10,10), sticky='nsew')
        entry_perc_low = ttk.Entry(tab, textvariable=self.perc_low, width=5)
        entry_perc_low.grid(row=4, column=2, padx=10, pady=(10,10), sticky='nsew')
        entry_perc_high = ttk.Entry(tab, textvariable=self.perc_high, width=5)
        entry_perc_high.grid(row=4, column=6, padx=10, pady=(10,10), sticky='nsew')
        ttk.Button(tab, text='Reset', command=self.reset, width=5, bootstyle=WARNING).grid(row=1, rowspan=4, column=10, padx=10, pady=(10,0), sticky='nsew')

        self.setpoint_low.trace_add("write", self.on_change)
        self.setpoint_high.trace_add("write", self.on_change)
        self.offset.trace_add("write", self.on_change)
        self.factor.trace_add("write", self.on_change)
        entry_perc_low.bind("<Return>", lambda event: self.calc_factor(False))
        entry_perc_high.bind("<Return>", lambda event: self.calc_factor(True))
        entry_adj_low.bind("<Return>",  lambda event: self.calc_perc(event, False))
        entry_adj_high.bind("<Return>", lambda event: self.calc_perc(event, True))

        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=11, padx=10, pady=(10,0), sticky='nsew')
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def lin_func(self):
            return (2 - float(self.factor.get())) * self.x + (float(self.offset.get()) * 1000), max((2 - float(self.factor.get())) * self.max_x + (float(self.offset.get()) * 1000), self.max_x)
        
    def redraw(self, event=None):
        self.calc_deltas()
        y, max_y = self.lin_func()
        self.adj_line.set_ydata(y)
        self.ax.set_xlim(float(self.setpoint_low.get()) - 100, float(self.setpoint_high.get()) + 100)
        self.ax.set_ylim([0, max_y + 100])
        if self.v_low: self.v_low.remove()
        if self.v_high: self.v_high.remove()
        self.v_low = self.ax.vlines(float(self.setpoint_low.get()), float(self.setpoint_low.get()), float(self.delta_low.get()), linestyle='--')
        self.v_high = self.ax.vlines(float(self.setpoint_high.get()), float(self.setpoint_high.get()), float(self.delta_high.get()), linestyle='--')
        self.sp_low_slider.configure(to=float(self.setpoint_high.get()))
        self.sp_high_slider.configure(from_=float(self.setpoint_low.get()))
        self.update_setpoint_annot()
        self.canvas.draw()

    def reset(self):
        self.factor.set(1.)
        self.offset.set(0.)
        self.perc_low.set(0.00)
        self.perc_high.set(0.00)
        self.redraw()

    def calc_deltas(self):
        self.delta_low.set("{:.2f}".format((2 - float(self.factor.get())) * float(self.setpoint_low.get()) + (float(self.offset.get()) * 1000)))
        self.delta_high.set("{:.2f}".format((2 - float(self.factor.get())) * float(self.setpoint_high.get()) + (float(self.offset.get()) * 1000)))

    def calc_factor(self, high):
        sp_l = self.setpoint_low.get()
        sp_h = self.setpoint_high.get()
        sp = self.setpoint_low.get()
        perc = self.perc_low.get()
        if high:
            perc = self.perc_high.get()
            sp = self.setpoint_high.get()

        delta = float(sp) * (1 + float(perc)/100)
        run = float(sp_h) - float(sp_l)
        rise = delta - float(self.delta_low.get()) if high else float(self.delta_high.get()) - delta
        slope = rise/run
        self.factor.set("{:.6f}".format(2 - slope))
        self.offset.set("{:.6f}".format((delta - slope*float(sp))/1000))
        self.redraw()

    def calc_perc(self, event, high):
        if high:
            self.perc_high.set((float(self.delta_high.get())-float(self.setpoint_high.get()))/float(self.setpoint_high.get())*100)
        else:
            self.perc_low.set((float(self.delta_low.get())-float(self.setpoint_low.get()))/float(self.setpoint_low.get())*100)
        self.calc_factor(high)

    def update_setpoint_annot(self):
        y0 = float(self.setpoint_low.get())
        y1 = float(self.delta_low.get())
        self.perc_low.set("{:.2f}".format((y1 - y0)*100/y0 if y0 != 0 else 0))
        self.annot_low.xy = (y0, y1)
        text = "Base: {:.2f}\nAdj: {:.2f}\n{}%".format(
            y0,y1,self.perc_low.get()
        )
        self.annot_low.set_text(text)
        self.annot_low.set_position((-y0/self.max_x*200 - 20, 30 - (y0/self.max_x*100)/2))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_low.get_bbox_patch().set_alpha(0.4)

        y1 = float(self.delta_high.get())
        y0 = float(self.setpoint_high.get())
        self.perc_high.set("{:.2f}".format((y1 - y0)*100/y0 if y0 != 0 else 0))
        self.annot_high.xy = (y0, y1)
        text = "Base: {:.2f}\nAdj: {:.2f}\n{}%".format(
            y0,y1,self.perc_high.get()
        )
        self.annot_high.set_text(text)
        self.annot_high.set_position((-y0/self.max_x*300 + 70, 110 - (y0/self.max_x*100)*1.3))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_high.get_bbox_patch().set_alpha(0.4)

    def update_annot(self, ind):
        adj_x,adj_y = self.adj_line.get_data()
        _,base_y = self.base_line.get_data()
        x0 = adj_x[ind["ind"][0]]
        y0 = adj_y[ind["ind"][0]]
        y1 = base_y[ind["ind"][0]]
        perc = (y0 - y1)*100/y1 if y0 != 0 else 0
        self.annot.xy = (x0, y0)
        text = "Base: {:.2f}\nAdj: {:.2f}\n{:.2f}%".format(
            x0,y0,perc
        )
        self.annot.set_text(text)
        self.annot.set_position((-y1/self.max_x*400 - 20, 150 - (y1/self.max_x*200)))
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.adj_line.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def on_change(self, *args):
        try:
            float(self.setpoint_low.get())
            float(self.setpoint_high.get())
            float(self.offset.get())
            float(self.factor.get())
            self.redraw()
        except:
            pass

    def on_sp_low_change(self, val):
        self.setpoint_low.set(int(float(val)))

    def on_sp_high_change(self, val):
        self.setpoint_high.set(int(float(val)))

    def on_offset_change(self, val):
        float_val = float(val)
        resolution = 0.000001
        stepped_val = round(float_val / resolution) * resolution
        self.offset.set("{:.6f}".format(float(stepped_val)))
        self.factor.set("{:.6f}".format(float(self.factor.get())))

    def on_factor_change(self, val):
        float_val = float(val)
        resolution = 0.000001
        stepped_val = round(float_val / resolution) * resolution
        self.offset.set("{:.6f}".format(float(self.offset.get())))
        self.factor.set("{:.6f}".format(stepped_val))


