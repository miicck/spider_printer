#!/usr/bin/python3.7
from spider import Spider
import numpy as np
import sys

radius = float(sys.argv[1])

s = Spider()

x, y = 0.0, 0.0
for angle in np.linspace(0, 2*np.pi, 100):
    new_x, new_y = radius * np.cos(angle), radius * np.sin(angle)
    dx, dy = new_x - x, new_y - y
    x, y = new_x, new_y
    s.move((dx, dy, 0))

new_x, new_y = 0.0, 0.0
dx, dy = new_x - x, new_y - y
s.move((dx, dy, 0))
