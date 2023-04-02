import RPi.GPIO as gp
import time
import threading
import queue

class StepperMotor:
    
    _GP_SETUP = False

    def __init__(self, step_pin: int, dir_pin: int, microstepping: int = 1):

        if not StepperMotor._GP_SETUP:
            gp.setmode(gp.BCM)
            StepperMotor._GP_SETUP = True

        gp.setup(step_pin, gp.OUT)
        gp.setup(dir_pin, gp.OUT)

        self._step_pin = step_pin
        self._dir_pin = dir_pin
        self._microstepping = microstepping
        self._target_position = 0.0
        self._actual_position = 0.0
        self._queue = queue.Queue()

        def control_loop():
            while True:
                n = self._queue.get()
                delta = n - self._actual_position
                self._rotate(delta)
                self._actual_position = n

        self._control_thread = threading.Thread(target=control_loop)
        self._control_thread.start()

    @property
    def target_position(self) -> float:
        return self._target_position

    def move_to(self, position: float):
        position = float(position)
        self._target_position = position
        self._queue.put(position)

    def rotate(self, revolutions: float):
        self.move_to(self.target_position + revolutions)
        
    def _rotate(self, revolutions: float):

        # Set direction pin
        gp.output(self._dir_pin, gp.HIGH if revolutions < 0 else gp.LOW)
        revolutions = abs(revolutions)

        # Work out number of steps/delay
        steps_per_revolution = 200 * self._microstepping
        steps = round(revolutions * steps_per_revolution)
        delay = 1.0 / (3.0 * steps_per_revolution)

        print(steps)

        # Make steps
        for n in range(steps):
            self._step(delay)

    def _step(self, delay: float):

        # Make a single step pulse
        gp.output(self._step_pin, gp.HIGH)
        time.sleep(delay/2)
        gp.output(self._step_pin, gp.LOW)
        time.sleep(delay/2)

    def __del__(self):
        print("Cleanup...")
        if StepperMotor._GP_SETUP:
            gp.cleanup()
            StepperMotor._GP_SETUP = False

# The usual suspects
alice = StepperMotor(2, 3)
bob = StepperMotor(17, 27)
carlos = StepperMotor(10, 11)
