#!/usr/bin/python3.7
from stepper import StepperMotor
from clothes_line import ClothesLine
import numpy as np

line = ClothesLine(
    StepperMotor(2, 3),
    StepperMotor(17, 27)
)

radius = 2.0

xy_moves_only = True
if xy_moves_only:
    angles = np.linspace(0, 2*np.pi, 100)

    xs, ys = radius*np.cos(angles), radius*np.sin(angles)

    # Move to start point
    line.move_to(radius, 0)

    # Move around circle
    for i in range(1, len(xs)):
        line.move_to(xs[i], ys[i-1])
        line.move_to(xs[i], ys[i])
    
    quit()


for angle in np.linspace(0, 2*np.pi, 100):
    x, y = radius * np.cos(angle), radius * np.sin(angle)
    x -= 2.0
    print(x, y)
    line.move_to(x, y)
