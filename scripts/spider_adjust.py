#!/usr/bin/python3.7
import sys
from stepper import alice, bob, carlos

motors = {
    "a": alice,
    "b": bob,
    "c": carlos
}
    
last_cmd = "a 1"

while True:
    cmd = input().strip()
    if cmd != "":
        last_cmd = cmd

    name, amt = last_cmd.split()
    print(name, amt)
    if name == "t":
        for m in motors:
            print(m, float(amt))
            motors[m].rotate(float(amt))
    else:
        motors[name].rotate(float(amt))
