import math

class Delta:
    def __init__(self):
        self.__delta = {
            'R' : 0.0,
            'T' : 0.0,
            'X' : 0.0,
            'Y' : 0.0
        }
    
    def calculate_delta(self, ecc_r_raw, ecc_t_raw, stn_r, stn_t_raw, is_aligner, adjustment):
        is_three_sixty = stn_t_raw == 360000
        stn_t_raw = stn_t_raw % 360000
        PI = math.pi
        # Adjust for aligner vs station handoff
        flange_adjust = 0 if is_aligner else PI
        # Delta calculation
        ecc_t_flange = PI - (ecc_t_raw/10)*PI/180
        ecc_r = (ecc_r_raw / 10) * 25.4
        stn_t_abs = 2 * PI - (stn_t_raw / 1000) * PI / 180
        ecc_t_abs = ecc_t_flange - flange_adjust + stn_t_abs
        ecc_x = ecc_r * math.cos(ecc_t_abs) * adjustment
        ecc_y = ecc_r * math.sin(ecc_t_abs) * adjustment
        stn_x = stn_r * math.cos(stn_t_abs)
        stn_y = stn_r * math.sin(stn_t_abs)
        waf_x = stn_x + ecc_x
        waf_y = stn_y + ecc_y
        waf_r = math.sqrt(waf_x * waf_x + waf_y * waf_y)
        waf_t_ten = math.atan(waf_y / waf_x) if waf_x != 0 else 0
        waf_r_stn = math.floor((waf_r - stn_r) + stn_r)
        waf_t_stn = math.floor(-1 * (waf_t_ten * 180 / PI) * 1000)
        # Store x,y values for GUI representation
        self.__delta['X'] = (ecc_r * math.sin(ecc_t_flange)) * adjustment
        self.__delta['Y'] = (-ecc_r * math.cos(ecc_t_flange)) * adjustment
        # Correct angles according to quadrants
        # print("stn_t_raw:", stn_t_raw, ", ecc_t_flange:", ecc_t_flange, ", waf_t_stn:", waf_t_stn)
        waf_t_final = 0

        if (((stn_t_raw >= 0 and stn_t_raw <= 90000) or (stn_t_raw > 270000 and stn_t_raw <= 360000)) and waf_t_stn > 0):
            waf_t_final = waf_t_stn
        elif (((stn_t_raw >= 0 and stn_t_raw < 90000) or (stn_t_raw >= 270000 and stn_t_raw <= 360000)) and waf_t_stn < 0):
            waf_t_final = 360000 + waf_t_stn
        elif (stn_t_raw >= 90000 and stn_t_raw <= 270000):
             waf_t_final = 180000 + waf_t_stn
        if waf_t_final == 0 and is_three_sixty:
            waf_t_final = 360000

        # Store r,t for updated robot parameters
        self.__delta['R'] = waf_r_stn
        self.__delta['T'] = waf_t_final

    def get_r(self):
        return round(self.__delta.get('R'))
    
    def get_t(self):
        return round(self.__delta.get('T'))
    
    def get_x(self):
        return self.__delta.get('X')
    
    def get_y(self):
        return self.__delta.get('Y')



