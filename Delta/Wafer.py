import tkinter as tk
from tkinter import ttk
import Delta.DeltaConstants as dc
import Constants as c

class Wafer:
    def __init__(self, root, size):
        self.offset = 10
        self.marker_radius = 1.5
        self.triangle_side_len = 5
        self.radius=size
        self.diameter=self.radius*2
        self.waf_canvas = tk.Canvas(root, width=self.diameter+20, height=self.diameter+20)
        self.zoom_line = self.waf_canvas.create_rectangle(self.diameter + 100, self.radius - self.offset, 100, self.radius + 3 * self.offset, fill=c.COLORS["warning"])
        self.zoom_line = self.waf_canvas.create_rectangle(self.diameter - 90, 0, 100, self.radius + 3 * self.offset, fill=c.COLORS["secondary"])
        self.waf = self.waf_canvas.create_oval(self.offset, self.offset, self.diameter+self.offset, self.diameter+self.offset,  fill=c.COLORS["selectbg"], outline=c.COLORS["selectbg"])
        self.zoom_line = self.waf_canvas.create_oval(self.diameter - (self.radius-self.radius*1/4)+self.offset, 
                                                     self.diameter - (self.radius-self.radius*1/4)+self.offset, 
                                                     self.diameter - (self.radius+self.radius*1/4)+self.offset, 
                                                     self.diameter - (self.radius+self.radius*1/4)+self.offset, 
                                                     outline=c.COLORS["primary"])     
        self.center = self.waf_canvas.create_oval(self.radius- self.marker_radius+self.offset, self.radius+ self.marker_radius+self.offset, 
                                                  self.radius+ self.marker_radius+self.offset, self.radius- self.marker_radius+self.offset, fill=c.COLORS["inputbg"])
        self.notch = self.waf_canvas.create_polygon(self.radius-self.triangle_side_len+self.offset, self.offset, self.radius+self.triangle_side_len, self.offset, self.radius, self.triangle_side_len, fill='red')
        self.delta = None
        self.stn = ttk.Label(self.waf_canvas, text="Station Adjustment")
        self.waf_canvas.pack(fill="both", expand=True)

    # Change wafer notch post position on GUI
    def change_position(self, position):
        self.waf_canvas.delete(self.notch)
        if (position):
            if position == dc.ZERO:
                self.notch = self.waf_canvas.create_polygon(self.diameter+self.offset, 
                                                            self.radius+self.triangle_side_len+self.offset, 
                                                            self.diameter+self.offset, 
                                                            self.radius-self.triangle_side_len+self.offset, 
                                                            self.diameter-2*self.triangle_side_len+self.offset, 
                                                            self.radius+self.offset, 
                                                            fill=c.COLORS["primary"])
            elif position == dc.TWO_SEVENTY:
                self.notch = self.waf_canvas.create_polygon(self.radius-self.triangle_side_len+self.offset, 
                                                            self.diameter+self.offset, 
                                                            self.radius+self.triangle_side_len+self.offset, 
                                                            self.diameter+self.offset, 
                                                            self.radius+self.offset, 
                                                            self.diameter-2*self.triangle_side_len+self.offset, 
                                                            fill=c.COLORS["primary"])
            elif position == dc.ONE_EIGHTY:
                self.notch = self.waf_canvas.create_polygon(self.offset, self.radius+self.triangle_side_len+self.offset, 
                                                            self.offset, 
                                                            self.radius-self.triangle_side_len+self.offset, 
                                                            2*self.triangle_side_len+self.offset, 
                                                            self.radius+self.offset, 
                                                            fill=c.COLORS["primary"])
            else:
                self.notch = self.waf_canvas.create_polygon(self.radius-self.triangle_side_len+self.offset, 
                                                            self.offset, self.radius+self.triangle_side_len+self.offset, 
                                                            self.offset, self.radius+self.offset, 
                                                            2*self.triangle_side_len+self.offset, 
                                                            fill=c.COLORS["primary"])

    # Add Delta marker to GUI
    def add_delta(self, x, y, size, zoom):
        self.waf_canvas.delete(self.delta)
        self.waf_canvas.delete(self.zoom_line)
        x = round(x, 1)/1000
        y = round(y, 1)/1000
        self.zoom_line = self.waf_canvas.create_oval(self.diameter - (self.radius-self.radius*zoom/4)+self.offset, 
                                                     self.diameter - (self.radius-self.radius*zoom/4)+self.offset, 
                                                     self.diameter - (self.radius+self.radius*zoom/4)+self.offset, 
                                                     self.diameter - (self.radius+self.radius*zoom/4)+self.offset, 
                                                     outline=c.COLORS["primary"])   
        self.delta = self.waf_canvas.create_oval(round((self.radius- self.marker_radius)-(self.radius/(size/2)*x*zoom)+self.offset, 1), 
                                                round((self.radius+ self.marker_radius)+(self.radius/(size/2)*y*zoom)+self.offset, 1), 
                                                round((self.radius+ self.marker_radius)-(self.radius/(size/2)*x*zoom)+self.offset, 1), 
                                                round((self.radius- self.marker_radius)+(self.radius/(size/2)*y*zoom)+self.offset, 1), fill=c.COLORS["primary"], outline="")      

    # Remove Delta marker from GUI
    def remove_delta(self):
        self.waf_canvas.delete(self.delta)