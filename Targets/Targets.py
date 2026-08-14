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
    def __init__(self, root, num_targets, eotl):
        self.root = root
        self.ovals = []
        self.targets = []
        self.w_h = CANVAS_PADDING * num_targets + CANVAS_BASE_SIZE
        self.cmap = self._build_colormap(eotl)

        self._build_canvas(root)
        self._build_colorbar(root)
        self.draw_targets(num_targets)

# ------------------------------------------------------------------ #
#  Initialization                                                      #
# ------------------------------------------------------------------ #

    def _build_colormap(self, danger_pct: float = 70.0) -> mcolors.LinearSegmentedColormap:
        """Build a wear-level colormap where danger color begins at danger_pct.

        Args:
            danger_pct: Percentage (0–100) at which the danger color starts.
        """
        threshold = max(0.01, min(danger_pct / 100.0, 0.99))  # clamp to (0.01, 0.99)

        color_stops = [
            (0.0,                  c.COLORS["light"]),
            (threshold * 0.33,     c.COLORS["success"]),
            (threshold * 0.66,     c.COLORS["primary"]),
            (threshold,            c.COLORS["warning"]),
            (threshold + (1.0 - threshold) * 0.5, c.COLORS["danger"]),
            (1.0,                  c.COLORS["danger"]),
        ]

        positions = [stop[0] for stop in color_stops]
        colors    = [stop[1] for stop in color_stops]

        return mcolors.LinearSegmentedColormap.from_list(
            "target_wear",
            list(zip(positions, colors))
        )


    def _build_canvas(self, root: tk.Widget):
        """Create the tk.Canvas that targets are drawn on."""
        frame = ttk.Frame(root)
        frame.grid(row=0, column=0, padx=5, pady=20, sticky="nesw")
        self.canvas = tk.Canvas(frame, width=self.w_h, height=self.w_h)
        self.canvas.grid(row=0, column=0)

    def _build_colorbar(self, root: tk.Widget):
        """Create and embed the matplotlib colorbar legend."""
        self.colorbar_root = root          # <-- store root for refresh
        gradient = np.linspace(0, 1, GRADIENT_STEPS).reshape(-1, 1)

        self.fig, self.ax_cb = plt.subplots(figsize=COLORBAR_FIGSIZE)
        self._draw_colorbar(gradient)

        self.colorbar_canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.colorbar_canvas.draw()
        self.colorbar_canvas.get_tk_widget().grid(row=0, column=1, sticky="ew")

    def _draw_colorbar(self, gradient: np.ndarray):
        """Draw the colorbar content onto self.ax_cb using the current colormap."""
        self.ax_cb.clear()
        self.ax_cb.imshow(gradient, aspect="auto", cmap=self.cmap)
        self.ax_cb.get_xaxis().set_visible(False)
        self.ax_cb.set_ylim([0, GRADIENT_STEPS])
        self.fig.set_facecolor(c.COLORS["bg"])
        self.ax_cb.set_facecolor(c.COLORS["bg"])
        self.ax_cb.tick_params(axis="both", colors=c.COLORS["inputfg"])
        for spine in self.ax_cb.spines.values():
            spine.set_color(c.COLORS["inputfg"])
        self.fig.tight_layout()

    def _refresh_colorbar(self):
        """Redraw the colorbar with the current colormap and update the canvas."""
        gradient = np.linspace(0, 1, GRADIENT_STEPS).reshape(-1, 1)
        self._draw_colorbar(gradient)
        self.colorbar_canvas.draw()

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

    def set_danger_threshold(self, eotl: float):
        """Rebuild the colormap with a new danger threshold and refresh all targets.

        Args:
            eotl: Percentage (0–100) at which the danger color starts.
        """
        self.cmap = self._build_colormap(eotl)
        self._refresh_colorbar()          
        self.change_color(self.targets) 
        

    def change_color(self, targets):
        """Update each oval's fill color based on its wear percentage variable."""
        self.targets = targets
        for oval, target_var in zip(self.ovals, targets):
             rgba = self.cmap(target_var.get()/100)
             color = mcolors.to_hex(rgba)
             self.canvas.itemconfig(oval, fill=color)