#!/usr/bin/python3.7
from stepper import StepperMotor
from clothes_line import ClothesLine
    
line = ClothesLine(
    StepperMotor(2, 3),
    StepperMotor(17, 27)
)

last_cmd = "w"
step_size = 0.5

while True:
    cmd = input().strip()
    if cmd != "":
        last_cmd = cmd

    x, y = line.position

    if last_cmd == "w":
        line.move_to(x, y+step_size)
    if last_cmd == "s":
        line.move_to(x, y-step_size)
    if last_cmd == "a":
        line.move_to(x-step_size, y)
    if last_cmd == "d":
        line.move_to(x+step_size, y)
