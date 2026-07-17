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