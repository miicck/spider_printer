#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np
import sys

radius = float(sys.argv[1])
s = Spider()
print(s.position)
z = s.initial_z
if len(sys.argv) > 2:
    z = float(sys.argv[2])

for angle in np.linspace(0, 2*np.pi, 512):
    s.position = [radius * np.cos(angle), radius * np.sin(angle), z]
