#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np

radius = 1.0

s = Spider()

s.position = ( radius,  radius, 0)
s.position = (-radius,  radius, 0)
s.position = (-radius, -radius, 0)
s.position = ( radius, -radius, 0)
s.position = ( radius,  radius, 0)
