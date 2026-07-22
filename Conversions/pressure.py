PRESSURE_UNITS = {
        "Pa": 1.0,
        "mPa": 0.001,
        "Bar": 100000.0,
        "mBar": 100.0,
        "Torr": 133.322368,
        "mTorr": 0.133322368,
        "atm": 101325.0,
        "inHg": 3386.3886,
        "psi": 6894.75729
    }
    

def convert_pressure(value, from_unit, to_unit):
    from_unit = from_unit.strip()
    to_unit = to_unit.strip()

    if from_unit not in PRESSURE_UNITS or to_unit not in PRESSURE_UNITS:
        raise ValueError(f"Unknown unit. Please use one of: {list(PRESSURE_UNITS.keys())}")

    value_in_pa = float(value) * PRESSURE_UNITS[from_unit]
    converted_value = value_in_pa / PRESSURE_UNITS[to_unit]
    return converted_value