import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import Constants as c

OVAL_WIDTH = 90
OVAL_HEIGHT = 120
OVAL_OUTLINE = 2
OVAL_START_ANGLE_OFFSET = 2 * math.pi / 3
GRADIENT_STEPS = 100
COLORBAR_FIGSIZE = (1, 4)
CANVAS_PADDING = 40 # extra px per target added to canvas size
CANVAS_BASE_SIZE = 150 # minimum canvas width/height

class Targets:
    def __init__(self, root, num_targets):
        self.root = root
        self.ovals = []
        self.w_h = CANVAS_PADDING * num_targets + CANVAS_BASE_SIZE
        self.cmap = self._build_colormap()

        self._build_canvas(root)
        self._build_colorbar(root)
        self.draw_targets(num_targets)

# ------------------------------------------------------------------ #
#  Initialization                                                      #
# ------------------------------------------------------------------ #

    def _build_colormap(self) -> mcolors.LinearSegmentedColormap:
        """Build and return the wear-level color gradient."""
        colors = [c.COLORS["light"],
                       c.COLORS["success"],
                       c.COLORS["primary"],
                       c.COLORS["warning"],
                       c.COLORS["danger"],
                       c.COLORS["danger"]
        ]
        return mcolors.LinearSegmentedColormap.from_list("custom_gradient", colors)

    def _build_canvas(self, root: tk.Widget):
        """Create the tk.Canvas that targets are drawn on."""
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, padx=5, pady=20, sticky="nesw")
        self.canvas = tk.Canvas(frame, width=self.w_h, height=self.w_h)
        self.canvas.grid(row=0, column=0)

    def _build_colorbar(self, root: tk.Widget):
        """Create and embed the matplotlib colorbar legend."""
        gradient = np.linspace(0, 1, 100).reshape(-1, 1)

        self.fig, ax = plt.subplots(figsize=COLORBAR_FIGSIZE)
        ax.imshow(gradient, aspect='auto', cmap=self.cmap)
        ax.get_xaxis().set_visible(False)
        ax.set_ylim([0, GRADIENT_STEPS])
        
        self.fig.set_facecolor(c.COLORS["bg"])
        ax.set_facecolor(c.COLORS["bg"])
        ax.tick_params(axis='both', colors=c.COLORS["inputfg"])
        for spine in ax.spines.values():
            spine.set_color(c.COLORS["inputfg"])

        plt.tight_layout()

        colorbar_canvas = FigureCanvasTkAgg(self.fig, master=root)
        colorbar_canvas.draw()
        colorbar_canvas.get_tk_widget().grid(row=0, column=1, sticky='ew')

# ------------------------------------------------------------------ #
#  Drawing                                                             #
# ------------------------------------------------------------------ #

    def draw_targets(self, num_targets):
        """Draw evenly-spaced target ovals on the canvas."""
        plt.close(self.fig)

        center_x = self.w_h / 2
        center_y = self.w_h / 2
        radius =  self.w_h / (4 - num_targets / 12) if num_targets > 1 else 0

        for i in range(num_targets):
            angle = i * (2 * math.pi / num_targets) - 2*math.pi/3
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            x0, y0 = x - (OVAL_WIDTH / 2), y - (OVAL_HEIGHT / 2)
            x1, y1 = x + (OVAL_WIDTH / 2), y + (OVAL_HEIGHT / 2)

            oval = self.canvas.create_oval(
                x0, y0, x1, y1, 
                outline = c.COLORS["dark"], 
                width   = OVAL_OUTLINE, 
                fill    = c.COLORS["light"],
            )
            self.ovals.append(oval)
            self.canvas.create_text(
                x, y, 
                text = str(i + 1), 
                fill = "black", 
                font = "Helvetica 12 bold",
            )

    def change_color(self, targets):
        """Update each oval's fill color based on its wear percentage variable."""
        for oval, target_var in zip(self.ovals, targets):
             rgba = self.cmap(target_var.get()/100)
             color = mcolors.to_hex(rgba)
             self.canvas.itemconfig(oval, fill=color)