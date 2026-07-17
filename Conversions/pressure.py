pressure_units = ["Torr", "mTorr", "Bar", "mBar", "Pa", "mPa", "inHg", "psi", "atm"] 

#Pressure Caluculations
def toMilli(input):
    return input * 1000

def toNom(input):
    return input / 1000

#Torr to ...
def torrToBar(input):
    return input / 750.061682704

def torrToPa(input):
    return input * 133.3223684211

def torrToInhg(input):
    return input / 25.4

def torrToPsi(input):
    return input / 51.715

def torrToAtm(input):
    return input / 760

#Bar to ...
def barToTorr(input):
    return input * 750.061682704

def barToPa(input):
    return input * 100000

def barToInhg(input):
    return input * 29.53

def barToPsi(input):
    return input * 14.5038

def barToAtm(input):
    return input / 1.013

#Pa to ...
def paToTorr(input):
    return input * 0.0075006168

def paToBar(input):
    return input * 1.0E-5

def paToInhg(input):
    return input / 3386

def paToPsi(input):
    return input / 6895

def paToAtm(input):
    return input / 101300

#inHg to ...
def inhgToTorr(input):
    return input * 25.4

def inhgToBar(input):
    return input / 29.53

def inhgToPa(input):
    return input * 3386

def inhgToPsi(input):
    return input / 2.036

def inhgToAtm(input):
    return input / 29.921


#PSI to ...
def psiToTorr(input):
    return input * 51.715

def psiToBar(input):
    return input / 14.5038 

def psiToPa(input):
    return input * 6895

def psiToInhg(input):
    return input * 2.036

def psiToAtm(input):
    return input / 14.696

#ATM to ..
def atmToTorr(input):
    return input * 760

def atmToBar(input):
    return input * 1.013

def atmToPa(input):
    return input * 101300

def atmToInhg(input):
    return input * 29.921

def atmToPsi(input):
    return input * 14.696

def convert_pressure(input_units, output_units, input):
    try:
        input = float(input)
    except ValueError:
        return 0
    
    if input_units[0] == 'm' and output_units[0] != 'm':
        input = toNom(input)
        input_units = input_units[1:]
    elif input_units[0] != 'm' and output_units[0] == 'm':
        input = toMilli(input)
        out_type = out_type[1:]
    elif input_units[0] == 'm' and output_units[0] == 'm':
        input_units = input_units[1:]
        output_units = output_units[1:]

    if input_units == "Torr":
        if output_units == "Bar":
            return torrToBar(input)
        elif output_units == "Pa":
            return torrToPa(input)
        elif output_units == "inHg":
            return torrToInhg(input)
        elif output_units == "psi":
            return torrToPsi(input)
        elif output_units == "atm":
            return torrToAtm(input)
    elif input_units == "Bar":
        if output_units == "Torr":
            return barToTorr(input)
        elif output_units == "Pa":
            return barToPa(input)
        elif output_units == "inHg":
            return barToInhg(input)
        elif output_units == "psi":
            return barToPsi(input)
        elif output_units == "atm":
            return barToAtm(input)
    elif input_units == "Pa":
        if output_units == "Torr":
            return paToTorr(input)
        elif output_units == "Bar":
            return paToBar(input)
        elif output_units == "inHg":
            return paToInhg(input)
        elif output_units == "psi":
            return paToPsi(input)
        elif output_units == "atm":
            return paToAtm(input)
    elif input_units == "inHg":
        if output_units == "Torr":
            return inhgToTorr(input)
        elif output_units == "Bar":
            return inhgToBar(input)
        elif output_units == "Pa":
            return inhgToPa(input)
        elif output_units == "psi":
            return inhgToPsi(input)
        elif output_units == "atm":
            return inhgToAtm(input)
    elif input_units == "psi":
        if output_units == "Torr":
            return psiToTorr(input)
        elif output_units == "Bar":
            return psiToBar(input)
        elif output_units == "Pa":
            return psiToPa(input)
        elif output_units == "inHg":
            return psiToInhg(input)
        elif output_units == "atm":
            return psiToAtm(input)
    elif input_units == "atm":
        if output_units == "Torr":
            return atmToTorr(input)
        elif output_units == "Bar":
            return atmToBar(input)
        elif output_units == "Pa":
            return atmToPa(input)
        elif output_units == "inHg":
            return atmToInhg(input)
        elif output_units == "psi":
            return atmToPsi(input)
    else:
        return input