#!/usr/bin/python3.7
from stepper import alice, bob, carlos
import sys
import time

up = False
step_size = 0.1
delay = 1

motor = {"a": alice, "b": bob, "c": carlos}[sys.argv[1]]

while True:

    if up:
        motor.rotate(step_size)
    else:
        motor.rotate(-step_size)

    up = not up
    time.sleep(delay)
