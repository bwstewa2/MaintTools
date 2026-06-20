import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import Delta.DeltaCalculation, Delta.Wafer, Delta.History, Delta.Settings
import Delta.DeltaConstants as dc

class Delta_Panel:
    def __init__(self):
        self.history = Delta.History.History()
        self.history.read()
        self.settings = Delta.Settings.Settings()
        self.settings.read()

        tools = []
        for tool in self.history.get():
            tools.append(tool['tool'])

        self.delta = Delta.DeltaCalculation.Delta()
        self.tool = ttk.Variable()
        self.stn_r = ttk.IntVar()
        self.stn_t = ttk.IntVar()
        self.ecc_r = ttk.IntVar()
        self.ecc_t = ttk.IntVar()
        self.result_r = ttk.IntVar()
        self.result_t = ttk.IntVar()
        self.ws = ttk.Variable(value=str(self.settings.get()['ws']))
        self.pp = ttk.Variable(value=str(self.settings.get()['pp']))
        self.ds = ttk.DoubleVar(value=str(self.settings.get()['ds']))
        self.ia = ttk.IntVar(value=int(self.settings.get()['ia']))
        self.zoom = ttk.DoubleVar(value="{:.2f}".format(1))
        self.history_index = ttk.IntVar(value=len(self.history.get()))

    def create(self, tab):    
        frame = ttk.Frame(tab)
        frame1 = ttk.Frame(frame)
        frame1.grid(row=0, column=0, pady=(20,0), padx=5, sticky="nsew")
        frame2 = ttk.Frame(frame)
        frame2.grid(row=1, column=0, pady=(10,0), padx=5, sticky="nsew")
        frame3 = ttk.Frame(frame1)
        frame3.grid(row=9, column=0, columnspan=2, pady=(0,0), padx=5, sticky="nsew")
        frame4 = ttk.Frame(frame)
        frame4.grid(row=0, column=5, rowspan=5, pady=(10,10), padx=5, sticky="nsew")
        frame5 = ttk.Frame(frame2)
        frame5.grid(row=0, column=1, sticky="nsew")

        ttk.Label(frame1, text='Tool: ', width=20).grid(row=0, column=0, padx=5, pady=(20,0), sticky='nsew')
        ttk.Label(frame1, text='Aligner R (10th mil): ', width=20).grid(row=1, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='Aligner T (10th deg): ', width=20).grid(row=2, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='Station R (micron): ', width=20).grid(row=3, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='Station T (1000th deg): ', width=20).grid(row=4, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='New Station R Value: ', width=20).grid(row=7, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='New Station T Value: ', width=20).grid(row=8, column=0, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='Delta Adjustment (sensitivity):', anchor='center').grid(row=5, column=0, columnspan=2, padx=5, pady=(10,0), sticky='nsew')
        ttk.Label(frame1, text='Zoom', anchor='center').grid(row=2, column=2, columnspan=1, padx=5, pady=(10,0), sticky='nsew')

        tool_entry = ttk.Combobox(frame1, textvariable=self.tool, width=15, values=list(set([str(tool['tool']) for tool in self.history.get() if str(tool['tool']) != ''])))
        tool_entry.grid(row=0, column=1, padx=5, pady=(10,0), sticky='nsew')
        ws_entry = ttk.Combobox(frame1, textvariable=self.ws, values=['6\"', '8\"'], width=4)
        ws_entry.grid(row=0, column=2, padx=5, pady=(10,0), sticky='nsew')
        self.pp_entry = ttk.Combobox(frame1, textvariable=self.pp, values=[dc.ZERO, dc.NINTY, dc.ONE_EIGHTY, dc.TWO_SEVENTY], width=4)
        self.pp_entry.grid(row=1, column=2, padx=5, pady=(10,0), sticky='nsew')
        ecc_r_entry = ttk.Entry(frame1, textvariable=self.ecc_r, width=15)
        ecc_r_entry.grid(row=1, column=1, padx=5, pady=(10,0), sticky='nsew')
        ecc_t_entry = ttk.Entry(frame1, textvariable=self.ecc_t, width=15)
        ecc_t_entry.grid(row=2, column=1, padx=5, pady=(10,0), sticky='nsew')
        stn_r_entry = ttk.Entry(frame1, textvariable=self.stn_r, width=15)
        stn_r_entry.grid(row=3, column=1, padx=5, pady=(10,0), sticky='nsew')
        stn_t_entry = ttk.Entry(frame1, textvariable=self.stn_t, width=15)
        stn_t_entry.grid(row=4, column=1, padx=5, pady=(10,10), sticky='nsew')
        result_r_entry = ttk.Entry(frame1, textvariable=self.result_r, state='readonly')
        result_r_entry.grid(row=7, column=1, padx=5, pady=(10,0), sticky='nsew')
        result_t_entry = ttk.Entry(frame1, textvariable=self.result_t, state='readonly')
        result_t_entry.grid(row=8, column=1, padx=5, pady=(10,0), sticky='nsew')
        ds_entry = ttk.Entry(frame1, textvariable=self.ds, width=5)
        ds_entry.grid(row=5, column=2, padx=5, pady=(10,0), sticky='nsew')
        ds_slider = ttk.Scale(frame1, variable=self.ds, from_=0, to=1.5, orient='horizontal', length=50)
        ds_slider.grid(row=6, column=0, columnspan=2, padx=5, pady=(10,0), sticky='ew')
        zoom_slider = ttk.Scale(frame1, variable=self.zoom, from_=dc.ZOOM_MAX, to=dc.ZOOM_MIN, orient='vertical', length=50)
        zoom_slider.grid(row=3, column=2, rowspan=2, padx=5, pady=(10,0), sticky='ns')

        self.waf = Delta.Wafer.Wafer(frame4, dc.WAFER_IMAGE_SIZE)
        self.waf.change_position(self.settings.get()['pp'])

        ttk.Checkbutton(frame3, text='Aligner Position', variable=self.ia, command=self.checkbox_changed, compound='right').grid(row=0, column=0, padx=5, pady=(10,0), sticky='w')
        ttk.Button(frame1, text='Reset', command=self.reset, width=5, bootstyle=WARNING).grid(row=6, column=2, padx=5, pady=(10,0))
        ttk.Button(frame3, text='Calculate', command=lambda: self.calculate_enter(None), width=10).grid(row=0, column=1,  padx=5, pady=(10,0))
        ttk.Button(frame3, text='Clear', command=self.clear, bootstyle=WARNING, width=10).grid(row=0, column=2,  padx=5, pady=(10,0))
        ttk.Button(frame1, text='\u2192', command=self.history_fwd, width=5, style=INFO).grid(row=8, column=2, padx=5, pady=(10,0))
        ttk.Button(frame1, text='\u2190', command=self.history_back, width=5, style=INFO).grid(row=9, column=2, padx=5, pady=(10,0))
        ttk.Button(frame1, text='\u2934', command=self.set_results, width=5, style=INFO).grid(row=7, column=2, padx=5, pady=(10,0))

        ecc_r_entry.bind("<Return>", self.calculate_enter)
        stn_t_entry.bind("<Return>", self.calculate_enter)
        ecc_r_entry.bind("<Return>", self.calculate_enter)
        stn_t_entry.bind("<Return>", self.calculate_enter)
        self.pp_entry.bind("<<ComboboxSelected>>", self.update_settings)
        ws_entry.bind("<<ComboboxSelected>>", self.update_settings)
        ds_entry.bind("<<ComboboxSelected>>", self.update_settings)
        ds_slider.bind("<ButtonRelease-1>", self.update_settings)
        zoom_slider.bind("<ButtonRelease-1>", self.update_settings)
        frame.pack(fill="both", expand=True)

    def on_closing(self):
        self.history.write()
        self.settings.write()

    def reset(self):
        self.ds.set(1.0)
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        if dc.WAFER_SIZE[self.ws.get()]/self.zoom.get() == dc.WAFER_SIZE[self.ws.get()]:
            self.waf.change_position(self.pp_entry.get())
        else: 
            self.waf.change_position(None)
        self.calculate()

    def checkbox_changed(self): 
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        self.calculate()

    def calculate(self):
        try:
            self.ecc_r.set(int(self.ecc_r.get()))
            self.ecc_t.set(int(self.ecc_t.get()))
            self.stn_r.set(int(self.stn_r.get()))
            self.stn_t.set(int(self.stn_t.get()))
            self.delta.calculate_delta(self.ecc_r.get(), self.ecc_t.get(), self.stn_r.get(), self.stn_t.get(), self.ia.get(), self.ds.get())
            self.result_r.set(self.delta.get_r())
            self.result_t.set(self.delta.get_t())
            if self.ia.get():
                self.waf.add_delta(-self.delta.get_x(), -self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
            else:
                self.waf.add_delta(self.delta.get_x(), self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
        except:
            return
        
    def calculate_enter(self, event):
        self.calculate()
        self.history.add(self.tool.get(), self.ecc_r.get(), self.ecc_t.get(), self.stn_r.get(), self.stn_t.get(), 
                            self.result_r.get(), self.result_t.get(), self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        self.history_index.set(len(self.history.get())-1)

    def clear(self):
        self.tool.set(0)
        self.stn_r.set(0)
        self.stn_t.set(0)
        self.ecc_r.set(0)
        self.ecc_t.set(0)
        self.result_r.set(0)
        self.result_t.set(0)
        self.waf.remove_delta()

    def history_fwd(self):
        if self.history_index.get() < len(self.history.get())-1:
            self.history_index.set(self.history_index.get() + 1)
            self.tool.set(self.history.get()[self.history_index.get()]['tool'])
            self.ecc_r.set(self.history.get()[self.history_index.get()]['ecc_r'])
            self.ecc_t.set(self.history.get()[self.history_index.get()]['ecc_t'])
            self.stn_r.set(self.history.get()[self.history_index.get()]['stn_r'])
            self.stn_t.set(self.history.get()[self.history_index.get()]['stn_t'])
            self.pp.set(self.history.get()[self.history_index.get()]['pp'])
            self.ws.set(self.history.get()[self.history_index.get()]['ws'])
            self.ds.set(self.history.get()[self.history_index.get()]['ds'])
            self.ia.set(self.history.get()[self.history_index.get()]['ia'])
            self.delta.calculate_delta(self.ecc_r.get(), self.ecc_t.get(), self.stn_r.get(), self.stn_t.get(), self.ia.get(), self.ds.get())
            self.result_r.set(self.delta.get_r())
            self.result_t.set(self.delta.get_t())
            if self.ia.get():
                self.waf.add_delta(-self.delta.get_x(), -self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
            else:
                self.waf.add_delta(self.delta.get_x(), self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
            self.waf.change_position(self.pp_entry.get())
            self.calculate()
        else:
                self.clear()
                self.history_index.set(min(self.history_index.get() + 1, len(self.history.get())))

    def history_back(self):
        if self.history_index.get() > 0:
            self.history_index.set(self.history_index.get() - 1)
            try:
                self.tool.set(self.history.get()[self.history_index.get()]['tool'])
                self.ecc_r.set(self.history.get()[self.history_index.get()]['ecc_r'])
                self.ecc_t.set(self.history.get()[self.history_index.get()]['ecc_t'])
                self.stn_r.set(self.history.get()[self.history_index.get()]['stn_r'])
                self.stn_t.set(self.history.get()[self.history_index.get()]['stn_t'])
                self.pp.set(self.history.get()[self.history_index.get()]['pp'])
                self.ws.set(self.history.get()[self.history_index.get()]['ws'])
                self.ds.set(self.history.get()[self.history_index.get()]['ds'])
                self.ia.set(self.history.get()[self.history_index.get()]['ia'])
                self.delta.calculate_delta(self.ecc_r.get(), self.ecc_t.get(), self.stn_r.get(), self.stn_t.get(), self.ia.get(), self.ds.get())
                self.result_r.set(self.delta.get_r())
                self.result_t.set(self.delta.get_t())
                if self.ia.get():
                    self.waf.add_delta(-self.delta.get_x(), -self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
                else:
                    self.waf.add_delta(self.delta.get_x(), self.delta.get_y(), dc.WAFER_SIZE[self.ws.get()], self.zoom.get())
                self.waf.change_position(self.pp_entry.get())
                self.calculate()
            except:
                self.clear()

    def set_results(self):
        self.stn_r.set(self.result_r.get())
        self.stn_t.set(self.result_t.get())
        self.result_r.set(0)
        self.result_t.set(0)

    def update_settings(self, event):
        self.settings.change(self.pp.get(), self.ws.get(), self.ds.get(), self.ia.get())
        if dc.WAFER_SIZE[self.ws.get()]/self.zoom.get() == dc.WAFER_SIZE[self.ws.get()]:
            self.waf.change_position(self.pp_entry.get())
        else: 
            self.waf.change_position(None)
        self.calculate()
   

