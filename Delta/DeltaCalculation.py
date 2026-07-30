import math


### Constants ###
RAW_ANGLE_SCALE = 10       # tenths of degrees per degree
RAW_RADIUS_SCALE = 10      # tenths of mils per mil
MILS_PER_INCH = 25.4
RAW_ANGLE_MAX = 360_000    # raw units for a full 360-degree rotation

class Delta:
    def __init__(self):
        self._delta: dict[str, float] = {"R": 0.0, "T": 0.0, "X": 0.0, "Y": 0.0}
    
    # ------------------------------------------------------------------ #
    #  Public Interface                                                    #
    # ------------------------------------------------------------------ #

    def calculate_delta(
        self,
        ecc_r_raw:  int,
        ecc_t_raw:  int,
        stn_r:      float,
        stn_t_raw:  int,
        is_aligner: bool,
        adjustment: float,
    ) -> None:
        """Compute corrected R, T, X, and Y deltas from raw eccentricity inputs.

        Args:
            ecc_r_raw:   Raw eccentricity radius (tenths of mils).
            ecc_t_raw:   Raw eccentricity angle  (tenths of degrees).
            stn_r:       Station radius (mils).
            stn_t_raw:   Station angle in raw units. 360000 means exactly 360 degrees.
            is_aligner:  True if the source is an aligner; False for station handoff.
            adjustment:  Sign/scale correction applied to the eccentricity vector.
        """
        # --- Normalise inputs ---
        is_three_sixty = stn_t_raw == RAW_ANGLE_MAX
        stn_t_raw      = stn_t_raw % RAW_ANGLE_MAX

        # --- Convert raw units to radians / mils ---
        flange_adjust = 0.0 if is_aligner else math.pi
        ecc_r         = (ecc_r_raw / RAW_RADIUS_SCALE) * MILS_PER_INCH
        ecc_t_flange  = math.pi - (ecc_t_raw / RAW_ANGLE_SCALE) * math.pi / 180 - flange_adjust
        stn_t_abs     = 2 * math.pi - (stn_t_raw / 1000) * math.pi / 180

        # --- Compute wafer position vector ---
        ecc_t_abs = ecc_t_flange + stn_t_abs
        ecc_x     = ecc_r * math.cos(ecc_t_abs) * adjustment
        ecc_y     = ecc_r * math.sin(ecc_t_abs) * adjustment
        stn_x     = stn_r * math.cos(stn_t_abs)
        stn_y     = stn_r * math.sin(stn_t_abs)
        waf_x     = stn_x + ecc_x
        waf_y     = stn_y + ecc_y

        # --- Convert wafer vector to polar station coordinates ---
        waf_r     = math.sqrt(waf_x ** 2 + waf_y ** 2)
        waf_t_rad = math.atan2(waf_y, waf_x)
        waf_r_stn = math.floor(waf_r - stn_r + stn_r)
        waf_t_stn = math.floor(-(waf_t_rad * 180 / math.pi) * 1000)

        # --- Store X/Y components for GUI display ---
        self._delta["X"] = (ecc_r * math.sin(ecc_t_flange)) * adjustment
        self._delta["Y"] = (-ecc_r * math.cos(ecc_t_flange)) * adjustment

        # --- Store corrected R/T robot parameters ---
        self._delta["R"] = waf_r_stn
        self._delta["T"] = self._correct_angle(stn_t_raw, waf_t_stn, is_three_sixty)

    @property
    def r(self):
        return round(self._delta["R"])
    @property
    def t(self):
        return round(self._delta["T"])
    @property
    def x(self):
        return self._delta["X"]
    @property
    def y(self):
        return self._delta["Y"]

    # ------------------------------------------------------------------ #
    #  Private Helpers                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _correct_angle(stn_t_raw: int, waf_t_stn: int, is_three_sixty: bool) -> int:
        """Map the computed wafer angle to the correct quadrant in raw units.

        Args:
            stn_t_raw:      Station angle in raw units (already modded to < 360000).
            waf_t_stn:      Raw computed wafer angle before quadrant correction.
            is_three_sixty: Whether the original station angle was exactly 360000.

        Returns:
            Quadrant-corrected wafer angle in raw units.
        """
        in_q1_or_q4 = stn_t_raw <= 90_000 or stn_t_raw > 270_000

        if in_q1_or_q4 and waf_t_stn > 0:
            waf_t_final = waf_t_stn
        elif in_q1_or_q4 and waf_t_stn < 0:
            waf_t_final = RAW_ANGLE_MAX + waf_t_stn
        else:
            waf_t_final = 180_000 + waf_t_stn

        if waf_t_final == 0 and is_three_sixty:
            waf_t_final = RAW_ANGLE_MAX

        return waf_t_final



