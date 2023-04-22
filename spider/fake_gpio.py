class FakeGPIO:

    BCM = "BCM"
    OUT = "OUT"

    def __init__(self):
        pass

    def setmode(self, mode):
        print(f"Set GPIO mode to {mode}")

    def setup(self, pin, mode):
        print(f"Set pin {pin} to mode {mode}")

gp = FakeGPIO()
