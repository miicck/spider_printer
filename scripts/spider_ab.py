#!/usr/bin/python3.7
from spider import Spider
import time

s = Spider()
up = False
step_size = 0.5
delay = 1

while True:

    if up:
        s.move((0,step_size,0))
    else:
        s.move((0,-step_size,0))

    up = not up
    time.sleep(delay)
