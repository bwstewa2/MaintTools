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
        self.factor_entry = ttk.StringVar(value=1.0)
        self.offset_entry = ttk.StringVar(value=0.0)
        self.percent = ttk.DoubleVar(value=0.0)
        self.base_points = (200, 1200)
        self.max_x = 1500
        self.setpoint_low = ttk.StringVar(value=100)
        self.setpoint_high = ttk.StringVar(value=1000)
        self.setpoint_low_entry = ttk.StringVar(value=100)
        self.setpoint_high_entry = ttk.StringVar(value=1000)
        self.adj_low = ttk.StringVar(value=100)
        self.adj_high = ttk.StringVar(value=1000)
        self.v_low = None
        self.v_high = None
        self.perc_low = ttk.StringVar(value=0.00)
        self.perc_high = ttk.StringVar(value=0.00)
        self.mode = ttk.StringVar(value="Adjustment")

        self.x = np.linspace(0, self.max_x, self.max_x)
        y, _ = self.lin_func()
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.ax.set_xlim(float(self.setpoint_low.get()) - 100, float(self.setpoint_high.get()) + 100)
        self.ax.set_ylim([min(float(self.setpoint_low.get()), float(self.adj_low.get())) - 100, max(float(self.setpoint_high.get()), float(self.adj_high.get())) + 200])
        self.base_line, = self.ax.plot(self.x, y, label=f'Base', color=c.COLORS["warning"])
        self.adj_line, = self.ax.plot(self.x, y, label=f'Adjusted', color=c.COLORS["primary"])
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
        ttk.Label(tab, text="Mode:").grid(row=1, column=1, padx=5, pady=(10,0), sticky='nse')
        rb1 = ttk.Radiobutton(tab, text="Adjustment", variable=self.mode, value="Adjustment", style="Toolbutton", command=self.on_radio_change)
        rb1.grid(row=1, column=2, padx=(10,0), pady=(10,0), sticky='nse')
        rb2 = ttk.Radiobutton(tab, text="Correction", variable=self.mode, value="Correction", style="Toolbutton", command=self.on_radio_change)
        rb2.grid(row=1, column=3, padx=(0,10), pady=(10,0), sticky='nse')

        factor_label = ttk.Label(tab, text="Calibration Factor:")
        factor_label.grid(row=2, column=1, padx=5, pady=(10,0), sticky='nse')
        factor_slider = ttk.Scale(tab, variable=self.factor, from_=1.1, to=0.9, orient='horizontal', length=200, command=self.on_factor_change)
        factor_slider.grid(row=2, column=2, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        factor_entry = ttk.Entry(tab, textvariable=self.factor_entry, width=15)
        factor_entry.grid(row=2, column=4, padx=10, pady=(10,0), sticky='nsew')
        offset_label = ttk.Label(tab, text="Offset (1/1000th):")
        offset_label.grid(row=2, column=5, padx=5, pady=(10,0), sticky='nse')
        offset_slider = ttk.Scale(tab, variable=self.offset, from_=-0.5, to=0.5, orient='horizontal', length=200, command=self.on_offset_change)
        offset_slider.grid(row=2, column=6, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        offset_entry = ttk.Entry(tab, textvariable=self.offset_entry, width=15)
        offset_entry = ttk.Entry(tab, textvariable=self.offset_entry, width=15)
        offset_entry.grid(row=2, column=8, padx=10, pady=(10,0), sticky='nsew')
        ttk.Button(tab, text='Reset', command=self.reset, width=5, bootstyle=WARNING).grid(row=2, rowspan=4, column=10, padx=10, pady=(10,10), sticky='nsew')

        setpoint_low_label = ttk.Label(tab, text="Setpoint Low:")
        setpoint_low_label.grid(row=3, column=1, padx=5, pady=(10,0), sticky='nse')
        setpoint_high_label = ttk.Label(tab, text="Setpoint High:")
        setpoint_high_label.grid(row=3, column=5, padx=5, pady=(10,0), sticky='nse')
        self.sp_low_slider = ttk.Scale(tab, variable=self.setpoint_low, from_=0, to=int(float(self.setpoint_high.get()))-1, orient='horizontal', length=200, command=self.on_sp_low_change)
        self.sp_low_slider.grid(row=3, column=2, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        sp_low_entry = ttk.Entry(tab, textvariable=self.setpoint_low_entry, width=5)
        sp_low_entry.grid(row=3, column=4, padx=10, pady=(10,0), sticky='nsew')
        self.sp_high_slider = ttk.Scale(tab, variable=self.setpoint_high, from_=int(float(self.setpoint_low.get()))+1, to=self.max_x, orient='horizontal', length=200, command=self.on_sp_high_change)
        self.sp_high_slider.grid(row=3, column=6, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        sp_high_entry = ttk.Entry(tab, textvariable=self.setpoint_high_entry, width=5)
        sp_high_entry.grid(row=3, column=8, padx=10, pady=(10,0), sticky='nsew')

        low_factor_label = ttk.Label(tab, text="Percent Low:")
        low_factor_label.grid(row=4, column=1, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        high_factor_label = ttk.Label(tab, text="Percent High:")
        high_factor_label.grid(row=4, column=5, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        self.low_adj_label = ttk.Label(tab, text="Adjusted Low:")
        self.low_adj_label.grid(row=4, column=3, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        self.high_adj_label = ttk.Label(tab, text="Adjusted High:")
        self.high_adj_label.grid(row=4, column=7, columnspan=1, padx=5, pady=(10,10), sticky='nse')
        entry_adj_low = ttk.Entry(tab, textvariable=self.adj_low, width=5)
        entry_adj_low.grid(row=4, column=4, padx=10, pady=(10,10), sticky='nsew')
        entry_adj_high = ttk.Entry(tab, textvariable=self.adj_high, width=5)
        entry_adj_high.grid(row=4, column=8, padx=10, pady=(10,10), sticky='nsew')
        entry_perc_low = ttk.Entry(tab, textvariable=self.perc_low, width=5)
        entry_perc_low.grid(row=4, column=2, padx=10, pady=(10,10), sticky='nsew')
        entry_perc_high = ttk.Entry(tab, textvariable=self.perc_high, width=5)
        entry_perc_high.grid(row=4, column=6, padx=10, pady=(10,10), sticky='nsew')

        self.setpoint_low.trace_add("write", lambda *args, **kwargs: self.redraw())
        self.setpoint_high.trace_add("write", lambda *args, **kwargs: self.redraw())
        sp_low_entry.bind("<Return>", lambda _: self.on_sp_low_entry())
        sp_high_entry.bind("<Return>", lambda _: self.on_sp_high_entry())
        self.offset.trace_add("write", lambda *args, **kwargs: self.redraw())
        self.factor.trace_add("write", lambda *args, **kwargs: self.redraw())
        offset_entry.bind("<Return>", lambda *args, **kwargs: self.on_offset_entry())
        factor_entry.bind("<Return>", lambda *args, **kwargs: self.on_factor_entry())
        entry_perc_low.bind("<Return>", lambda event: self.calc_factor(False))
        entry_perc_high.bind("<Return>", lambda event: self.calc_factor(True))
        entry_adj_low.bind("<Return>",  lambda event: self.calc_perc(False))
        entry_adj_high.bind("<Return>", lambda event: self.calc_perc(True))

        self.canvas = FigureCanvasTkAgg(self.fig, master=tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=11, padx=10, pady=(10,0), sticky='nsew')
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

    def lin_func(self):
        return (2 - float(self.factor.get())) * self.x + (float(self.offset.get()) * 1000), max((2 - float(self.factor.get())) * self.max_x + (float(self.offset.get()) * 1000), self.max_x)

    def redraw(self, event=None):
        self.calc_deltas()
        y,_ = self.lin_func()
        self.adj_line.set_ydata(y)
        self.ax.set_xlim(float(self.setpoint_low.get()) - 100, float(self.setpoint_high.get()) + 100)
        self.ax.set_ylim([min(float(self.setpoint_low.get()), float(self.adj_low.get())) - 100, max(float(self.setpoint_high.get()), float(self.adj_high.get())) + 200])
        if self.v_low: self.v_low.remove()
        if self.v_high: self.v_high.remove()
        arrow_low = "<-" if (self.mode.get() != "Adjustment") else "->"
        arrow_high = "<-" if (self.mode.get() != "Adjustment") else "->"
        self.v_low = self.ax.annotate(
            "", 
            xy=(float(self.setpoint_low.get()), float(self.adj_low.get())), 
            xytext=(float(self.setpoint_low.get()), float(self.setpoint_low.get())),
            arrowprops=dict(arrowstyle=arrow_low, linestyle='--', lw=1.5, color=c.COLORS["info"])
        )

        self.v_high = self.ax.annotate(
            "", 
            xy=(float(self.setpoint_high.get()), float(self.adj_high.get())), 
            xytext=(float(self.setpoint_high.get()), float(self.setpoint_high.get())),
            arrowprops=dict(arrowstyle=arrow_high, linestyle='--', lw=1.5 , color=c.COLORS["info"])
        )
        self.sp_low_slider.configure(to=float(self.setpoint_high.get())-1)
        self.sp_high_slider.configure(from_=float(self.setpoint_low.get())+1)
        self.update_setpoint_annot()
        self.canvas.draw()

    def reset(self):
        self.factor.set(1.)
        self.offset.set(0.)
        self.perc_low.set(0.00)
        self.perc_high.set(0.00)
        self.factor_entry.set(1.)
        self.offset_entry.set(0.)
        self.redraw()

    def calc_deltas(self):
        try:
            self.adj_low.set("{:.2f}".format((2 - float(self.factor.get())) * float(self.setpoint_low.get()) + (float(self.offset.get()) * 1000)))
            self.adj_high.set("{:.2f}".format((2 - float(self.factor.get())) * float(self.setpoint_high.get()) + (float(self.offset.get()) * 1000)))
        except:
            pass

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
        rise = delta - float(self.adj_low.get()) if high else float(self.adj_high.get()) - delta
        slope = rise/run
        self.factor.set("{:.6f}".format(2 - slope))
        self.factor_entry.set(self.factor.get())
        self.offset.set("{:.6f}".format((delta - slope*float(sp))/1000))
        self.offset_entry.set(self.offset.get())
        self.redraw()

    def calc_perc(self, high):
        if high:
            self.perc_high.set((float(self.adj_high.get())-float(self.setpoint_high.get()))/float(self.setpoint_high.get())*100)
        else:
            self.perc_low.set((float(self.adj_low.get())-float(self.setpoint_low.get()))/float(self.setpoint_low.get())*100)
        self.calc_factor(high)

    def update_setpoint_annot(self):
        width_px, height_px = self.fig.get_size_inches() * self.fig.dpi
        y0 = float(self.setpoint_low.get())
        y1 = float(self.adj_low.get())
        self.perc_low.set("{:.2f}".format((y1 - y0)*100/y0 if y0 != 0 else 0))
        self.annot_low.xy = (y0, y1)
        if self.mode.get() == "Adjustment":
            self.annot_low.set_text("Base: {:.2f}\nAdj: {:.2f}\n{}%".format(y0,y1,self.perc_low.get()))
        else:
            self.annot_low.set_text("Base: {:.2f}\nAct: {:.2f}\n{}%".format(y0,y1,self.perc_low.get()))
        x, y = self.ax.transData.transform((y0, y1))
        x_y = (-float(x/3) + width_px/14, float(abs(height_px/10 - y/3)))
        self.annot_low.set_position(x_y)
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_low.get_bbox_patch().set_alpha(0.4)

        y0 = float(self.setpoint_high.get())
        y1 = float(self.adj_high.get())
        self.perc_high.set("{:.2f}".format((y1 - y0)*100/y0 if y0 != 0 else 0))
        self.annot_high.xy = (y0, y1)
        if self.mode.get() == "Adjustment":
            self.annot_high.set_text("Base: {:.2f}\nAdj: {:.2f}\n{}%".format(y0,y1,self.perc_high.get()))
        else:
            self.annot_high.set_text("Base: {:.2f}\nAct: {:.2f}\n{}%".format(y0,y1,self.perc_high.get()))
        x, y = self.ax.transData.transform((y0, y1))
        x_y = (float(-x/6) + width_px/14, float(abs(height_px/5 - y/3)))
        self.annot_high.set_position(x_y)
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot_high.get_bbox_patch().set_alpha(0.4)

    def update_annot(self, ind, x, y):
        _, height_px = self.fig.get_size_inches() * self.fig.dpi
        adj_x,adj_y = self.adj_line.get_data()
        _,base_y = self.base_line.get_data()
        x0 = adj_x[ind["ind"][0]]
        y0 = adj_y[ind["ind"][0]]
        y1 = base_y[ind["ind"][0]]
        perc = (y0 - y1)*400/y1 if y1 != 0 else 0
        self.annot.xy = (x0, y0)
        if self.mode.get() == "Adjustment":
            self.annot.set_text("Base: {:.2f}\nAdj: {:.2f}\n{:.2f}%".format(x0,y0,perc))
        else:
            self.annot.set_text("Base: {:.2f}\nAct: {:.2f}\n{:.2f}%".format(x0,y0,perc))
        x_y = (float(-x/3) + 50, float(abs(height_px/6 - y/6)))
        self.annot.set_position(x_y)
        self.annot.get_bbox_patch().set_facecolor(c.COLORS["info"])
        self.annot.get_bbox_patch().set_alpha(0.4)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            x, y = event.x, event.y
            cont, ind = self.adj_line.contains(event)
            if cont:
                self.update_annot(ind, x, y)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def on_sp_low_change(self, val):
        self.setpoint_low.set(int(float(val)))
        self.setpoint_low_entry.set(int(float(val)))
        self.redraw()

    def on_sp_high_change(self, val):
        self.setpoint_high.set(int(float(val)))
        self.setpoint_high_entry.set(int(float(val)))
        self.redraw()

    def on_sp_low_entry(self):
        try:
            val = int(float(self.setpoint_low_entry.get()))
            if val < 0: val = 0
            if val >= int(float(self.setpoint_high.get())): val = int(float(self.setpoint_high.get())) - 1
            self.on_sp_low_change(val)
        except:
            self.setpoint_low_entry.set(self.setpoint_low.get())
    
    def on_sp_high_entry(self):
        try:
            val = int(float(self.setpoint_high_entry.get()))
            if val <= int(float(self.setpoint_low.get())): val = int(float(self.setpoint_low.get())) + 1
            if val > self.max_x: val = self.max_x
            self.on_sp_high_change(val)
        except ValueError:
            self.setpoint_high_entry.set(self.setpoint_high.get())

    def on_offset_change(self, val):
        float_val = float(val)
        resolution = 0.000001
        stepped_val = round(float_val / resolution) * resolution
        self.offset.set("{:.6f}".format(float(stepped_val)))
        self.factor.set("{:.6f}".format(float(self.factor.get())))
        self.offset_entry.set("{:.6f}".format(float(stepped_val)))
        self.factor_entry.set("{:.6f}".format(float(self.factor.get())))

    def on_factor_change(self, val):
        float_val = float(val)
        resolution = 0.000001
        stepped_val = round(float_val / resolution) * resolution
        self.offset.set("{:.6f}".format(float(self.offset.get())))
        self.factor.set("{:.6f}".format(float(stepped_val)))
        self.offset_entry.set("{:.6f}".format(float(self.offset.get())))
        self.factor_entry.set("{:.6f}".format(float(stepped_val)))

    def on_offset_entry(self):
        try:
            val = float(self.offset_entry.get())
            if val > 0.5: val = 0.5
            if val < -0.5: val = -0.5
            self.on_offset_change(val)
        except ValueError:
            self.offset_entry.set(self.offset.get())
    
    def on_factor_entry(self):
        try:
            val = float(self.factor_entry.get())
            if val > 1.1: val = 1.1
            if val < 0.9: val = 0.9
            self.on_factor_change(val)
        except ValueError:
            self.factor_entry.set(self.factor.get())

    def on_radio_change(self):
        if self.mode.get() == "Adjustment":
            self.low_adj_label.config(text="Adjusted Low:")
            self.high_adj_label.config(text="Adjusted High:")
            self.adj_line.set_label("Adjusted")
        else:
            self.low_adj_label.config(text="Actual Low:")
            self.high_adj_label.config(text="Actual High:")
            self.adj_line.set_label("Actual")

        sp = self.setpoint_low.get()
        self.setpoint_low.set(self.adj_low.get())
        self.setpoint_low_entry.set(self.setpoint_low.get())
        self.adj_low.set(sp)
        self.calc_perc(False)

        sp = self.setpoint_high.get()
        self.setpoint_high.set(self.adj_high.get())
        self.setpoint_high_entry.set(self.setpoint_high.get())
        self.adj_high.set(sp)
        self.calc_perc(True)


