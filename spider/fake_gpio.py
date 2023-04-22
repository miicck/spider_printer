class FakeGPIO:

    BCM = "BCM"
    OUT = "OUT"
    LOW = "LOW"
    HIGH = "HIGH"

    def __init__(self):
        pass

    def setmode(self, mode):
        print(f"Set GPIO mode to {mode}")

    def setup(self, pin, mode):
        print(f"Set pin {pin} to mode {mode}")

    def output(self, pin, value):
        pass

gp = FakeGPIO()
