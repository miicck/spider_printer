#!/usr/bin/python3.7
import sys
from stepper import alice, bob, carlos

motor = {
    "a": alice,
    "b": bob,
    "c": carlos
}[sys.argv[1].strip()]
    
last_cmd = "w"

while True:
    cmd = input().strip()
    if cmd != "":
        last_cmd = cmd

    if last_cmd == "w":
        motor.rotate(0.25)
    if last_cmd == "s":
        motor.rotate(-0.25)
