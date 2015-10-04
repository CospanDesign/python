
from signal import Signal

class Source(Signal):

    def __init__(self, voltage, current = 0, real_impedance = 0, imaginary_impedance = 0):
        super(Source, self).init()
        self.V = voltage
        self.I = current
        self.RIMP = real_impedance
        self.JIMP = imaginary_impedance

        self.CURR_V = self.V
        self.CURR_I = self.I

class VoltageSource(Source):

    def __init__(self, voltage, real_impedance = 0, imaginary_impedance = 0):

        super(VoltageSource, self).init(voltage = voltage, current = 0, real_impedance = real_impedance, imaginary_impedance = imaginary_impedance)

    def step(current):
        self.CURR_I = current


        return (self.CURR_V, self.CURR_I)
