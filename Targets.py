import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import Constants as c

class Targets:
    def __init__(self, root, num_tar):
        self.root = root
        self.ovals = []
        self.w_h = 40 * num_tar + 150
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, padx=5, pady=20, sticky="nesw")
        self.canvas = tk.Canvas(frame, width=self.w_h, height=self.w_h)
        self.canvas.grid(row=0, column=0)
        
        self.colors = ["#A9BDBD","#44aca4","#bc951a","#d05e2f","#d95092","#d95092"]
        gradient = np.linspace(0, 1, 100).reshape(-1, 1)
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", self.colors)

        self.fig, ax = plt.subplots(figsize=(1, 4))
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        ax.get_xaxis().set_visible(False)
        ax.set_ylim([0, 100])
        plt.tight_layout()
        self.fig.set_facecolor(c.COLORS["bg"])
        ax.set_facecolor(c.COLORS["bg"])
        ax.tick_params(axis='both', colors=c.COLORS["inputfg"])
        for spine in ax.spines.values():
            spine.set_color(c.COLORS["inputfg"])
        canvas = FigureCanvasTkAgg(self.fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=1, sticky='ew')

        self.draw_targets(num_tar)

    def draw_targets(self, num_targets):
        plt.close(self.fig)
        center_x=self.w_h/2
        center_y=self.w_h/2
        radius=0 
        if num_targets > 1:
            radius = self.w_h/(4-num_targets/12)

        oval_width=90
        oval_height=120
        for i in range(num_targets):
            angle = i * (2 * math.pi / num_targets) - 2*math.pi/3
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            x0 = x - (oval_width / 2)
            y0 = y - (oval_height / 2)
            x1 = x + (oval_width / 2)
            y1 = y + (oval_height / 2)
            self.ovals.append(self.canvas.create_oval(x0, y0, x1, y1, outline=c.COLORS["dark"], width=2, fill=c.COLORS["light"]))
            self.canvas.create_text(x, y, text=i+1, fill="black", font=('Helvetica 12 bold'))

    def change_color(self, targets):
        for i in range(len(targets)):
             cmap = mcolors.LinearSegmentedColormap.from_list("custom", self.colors)
             rgba_color = cmap(targets[i].get()/100)
             self.canvas.itemconfig(self.ovals[i], fill= mcolors.to_hex(rgba_color))