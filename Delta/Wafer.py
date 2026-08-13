import tkinter as tk

import Constants as c
import Delta.DeltaConstants as dc


### Constants ###
OFFSET            = 10
MARKER_RADIUS     = 3
TRIANGLE_SIDE     = 5
DELTA_SCALE       = 1000
DEFAULT_ZOOM      = 0.25   # zoom/4 fraction used for the reference ring at zoom=1
ARROW_START       = 5
ARROW_END         = 20
TEXT_Y_OFFSET     = 35
TEXT_X_OFFSET     = 40

class Wafer:
    """Tkinter canvas widget that displays a wafer, notch position, and delta marker."""

    def __init__(self, root: tk.Widget, size: int):
        self.radius   = size
        self.diameter = size * 2

        self._build_canvas(root)
        self._draw_base()

        self._delta_item = None
        self.waf_canvas.pack(fill="both", expand=True)

    # ------------------------------------------------------------------ #
    #  Initialization                                                      #
    # ------------------------------------------------------------------ #

    def _build_canvas(self, root: tk.Widget):
        """Create the tk.Canvas sized to fit the wafer with offset padding."""
        self.waf_canvas = tk.Canvas(
            root,
            width=self.diameter  + OFFSET * 2,
            height=self.diameter + OFFSET * 2,
        )
        self.x_arrow = None
        self.y_arrow = None
        self.x_label = None
        self.y_label = None

    def _draw_base(self):
        """Draw the static base elements: robot arm, laser, wafer, center, zoom ring, and notch."""
        d, r, o, t = self.diameter, self.radius, OFFSET, TRIANGLE_SIDE

        # Robot arm and laser representations
        self.waf_canvas.create_rectangle(
            7 * d / 8 + o, d + 100, 1 * d / 8 + o, r + o,
            fill=c.COLORS["secondary"],
        )
        self.waf_canvas.create_rectangle(
            d + 100, r - o, 100, r + 3 * o,
            fill=c.COLORS["warning"],
        )

        # Wafer body
        self.waf_canvas.create_oval(
            o, o, d + o, d + o,
            fill=c.COLORS["selectbg"],
            outline=c.COLORS["selectbg"],
        )

        # Center marker
        self.waf_canvas.create_oval(
            r - MARKER_RADIUS + o,
            r - MARKER_RADIUS + o,
            r + MARKER_RADIUS + o,
            r + MARKER_RADIUS + o,
            fill=c.COLORS["inputbg"],
        )

        # Default zoom reference ring (zoom = 1)
        self._zoom_ring = self._make_zoom_ring(zoom=1.0)

        # Default notch (top — TWO_SEVENTY position)
        self._notch_item = self.waf_canvas.create_polygon(
            r - t + o, o,
            r + t + o, o,
            r + o, 2 * t + o,
            fill="red",
        )

    def _make_zoom_ring(self, zoom: float) -> int:
        """Draw and return the canvas ID of the zoom reference ring."""
        d, r, o = self.diameter, self.radius, OFFSET
        inset = r * zoom / 4
        return self.waf_canvas.create_oval(
            d - (r - inset) + o,
            d - (r - inset) + o,
            d - (r + inset) + o,
            d - (r + inset) + o,
            outline=c.COLORS["primary"],
        )

    # ------------------------------------------------------------------ #
    #  Public Interface                                                    #
    # ------------------------------------------------------------------ #

    def change_position(self, position: str | None):
        """Redraw the notch triangle at the given wafer flat/notch position.

        Args:
            position: One of dc.ZERO, dc.NINTY, dc.ONE_EIGHTY, dc.TWO_SEVENTY,
                      or None to remove the notch entirely.
        """
        self.waf_canvas.delete(self._notch_item)
        if not position:
            self._notch_item = None
            return

        d, r, o, t = self.diameter, self.radius, OFFSET, TRIANGLE_SIDE

        notch_coords = {
            dc.ZERO: [
                d + o,         r + t + o,
                d + o,         r - t + o,
                d - 2 * t + o, r + o,
            ],
            dc.NINTY: [
                r - t + o, d + o,
                r + t + o, d + o,
                r + o,     d - 2 * t + o,
            ],
            dc.ONE_EIGHTY: [
                o,         r + t + o,
                o,         r - t + o,
                2 * t + o, r + o,
            ],
            dc.TWO_SEVENTY: [
                r - t + o, o,
                r + t + o, o,
                r + o,     2 * t + o,
            ],
        }

        coords = notch_coords.get(position, notch_coords[dc.TWO_SEVENTY])
        self._notch_item = self.waf_canvas.create_polygon(
            *coords, fill=c.COLORS["primary"]
        )

    def add_delta(self, x: float, y: float, size: float, zoom: float, change_r: int, change_t: int):
        """Draw the delta position marker and update the zoom reference ring.

        Args:
            x:    Eccentricity X component (raw mils before scaling).
            y:    Eccentricity Y component (raw mils before scaling).
            size: Wafer diameter in mils used to calculate the display scale.
            zoom: Current zoom level — scales both the marker and ring.
        """
        self.waf_canvas.delete(self._delta_item)
        self.waf_canvas.delete(self._zoom_ring)

        x_mil = -x / DELTA_SCALE
        y_mil = -y / DELTA_SCALE
        scale = self.radius / (size / 2) * zoom

        cx = round(self.radius - scale * x_mil + OFFSET, 1)
        cy = round(self.radius + scale * y_mil + OFFSET, 1)

        self._zoom_ring  = self._make_zoom_ring(zoom)
        self._delta_item = self.waf_canvas.create_oval(
            cx - MARKER_RADIUS,
            cy - MARKER_RADIUS,
            cx + MARKER_RADIUS,
            cy + MARKER_RADIUS,
            outline=c.COLORS["primary"],
        )
        self._add_directions(cx, cy, change_r, change_t)

    def _add_directions(self, cx, cy, change_r, change_t):
        components = [self.x_arrow, self.y_arrow, self.x_label, self.y_label]
        for component in components:
            if component:  self.waf_canvas.delete(component)
        
        direction_x = 1 if change_t > 0 else -1
        direction_y = -1 if change_r > 0 else 1
        if change_r != 0:
            self.x_arrow = self.waf_canvas.create_line(
                cx,
                cy + ARROW_START * direction_y,
                cx,
                cy + ARROW_END * direction_y, 
                arrow=tk.LAST,
                fill=c.COLORS["primary"]
            )
            self.x_label = self.waf_canvas.create_text(cx, cy + TEXT_Y_OFFSET * direction_y, text=change_r, fill="white", font=("Arial", 10)) 
            
        if change_t != 0:
            self.y_arrow = self.waf_canvas.create_line(
                cx + ARROW_START * direction_x,
                cy,
                cx + ARROW_END * direction_x,
                cy, 
                arrow=tk.LAST,
                fill=c.COLORS["primary"]
            )
            self.y_label = self.waf_canvas.create_text(cx + TEXT_X_OFFSET * direction_x, cy, text=change_t, fill="white", font=("Arial", 10))

    def remove_delta(self):
        """Remove the delta position marker from the canvas."""
        self.waf_canvas.delete(self._delta_item)
        self._delta_item = None