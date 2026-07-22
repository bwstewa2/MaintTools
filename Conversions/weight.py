WEIGHT_UNITS = {
        "kg": 1.0,
        "g": 0.001,
        "mg": 0.000001,
        "lb": 0.45359237,
        "oz": 0.028349523125,
        "stone": 6.35029318,
        "ton": 907.18474,
    }

def convert_weight(value, from_unit, to_unit):
    from_unit = from_unit.strip()
    to_unit = to_unit.strip()

    if from_unit not in WEIGHT_UNITS or to_unit not in WEIGHT_UNITS:
        raise ValueError(f"Unknown unit. Please use one of: {list(WEIGHT_UNITS.keys())}")

    value_in_kg = float(value) * WEIGHT_UNITS[from_unit]
    converted_value = value_in_kg / WEIGHT_UNITS[to_unit]
    return converted_value