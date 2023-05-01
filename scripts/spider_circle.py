#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np
import sys

radius = float(sys.argv[1])

s = Spider()
for angle in np.linspace(0, 2*np.pi, 512):
    s.position = [radius * np.cos(angle), radius * np.sin(angle), s.initial_z]
