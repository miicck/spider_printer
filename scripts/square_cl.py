#!/usr/bin/python3.7
from stepper import StepperMotor
from clothes_line import ClothesLine
import numpy as np
import sys
import time

line = ClothesLine(
    StepperMotor(2, 3),
    StepperMotor(17, 27)
)

size = float(sys.argv[1])
repeats = int(sys.argv[2])

half = size / 2

line.move_to(0, half)

for n in range(repeats):
    line.move_to( half,  half)
    line.move_to( half, -half)
    line.move_to(-half, -half)
    line.move_to(-half,  half)
