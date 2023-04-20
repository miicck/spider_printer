#!/usr/bin/python3.7
from stepper import alice, bob, carlos
import sys
import time

up = False
step_size = 0.1
delay = 0.1

motors = {"a": [alice], "b": [bob], "c": [carlos], "t": [alice, bob, carlos]}[sys.argv[1]]
if len(sys.argv) > 2:
    step_size = float(sys.argv[2])

while True:

    if up:
        for m in motors:
            m.rotate(step_size)
    else:
        for m in motors:
            m.rotate(-step_size)

    up = not up
    time.sleep(delay)
