#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np

s = Spider()

while True:

    d = np.random.random(3)-0.5
    d[2] = 0.0
    d /= np.linalg.norm(d)

    s.position += d
    s.position -= d
