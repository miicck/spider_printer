class FakeGPIO:
    BCM = "BCM"
    OUT = "OUT"
    LOW = "LOW"
    HIGH = "HIGH"

    def __init__(self):
        pass

    def setmode(self, mode):
        pass

    def setup(self, pin, mode):
        pass

    def output(self, pin, value):
        pass
