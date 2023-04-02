from stepper import StepperMotor
from typing import Tuple

class ClothesLine:

    def __init__(self, left_motor: StepperMotor, right_motor: StepperMotor):
        self._l = left_motor
        self._r = right_motor

    @property
    def position(self) -> Tuple[float, float]:
        l, r = self._l.target_position, self._r.target_position
        return r - l, l + r

    def move_to(self, x: float, y: float):
        self._l.move_to((y - x)/2)
        self._r.move_to((y + x)/2)
