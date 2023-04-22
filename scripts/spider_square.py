#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np

radius = 1.0

s = Spider()

s.move((radius/2, 0, 0))
s.move((0, radius/2, 0))
s.move((-radius, 0, 0))
s.move((0, -radius, 0))
s.move((radius, 0, 0))
s.move((0, radius/2, 0))
s.move((-radius/2, 0, 0)) 

