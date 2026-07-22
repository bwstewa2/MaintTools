LENGTH_UNITS = {
    "km": 1000.0,
    "m": 1.0,
    "mm": 0.001,
    "cm": 0.01,
    "in": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,
    "mi": 1609.344,
    "nm": 1e-9,
    "micron": 1e-6,
    "angstrom": 1e-10,
    "mils": 0.0000254
}

def convert_length(value, from_unit, to_unit):
    from_unit = from_unit.strip()
    to_unit = to_unit.strip()

    if from_unit not in LENGTH_UNITS or to_unit not in LENGTH_UNITS:
        raise ValueError(f"Unknown unit. Please use one of: {list(LENGTH_UNITS.keys())}")
    
    value_in_meters = float(value) * LENGTH_UNITS[from_unit]
    converted_value = value_in_meters / LENGTH_UNITS[to_unit]
    return converted_value