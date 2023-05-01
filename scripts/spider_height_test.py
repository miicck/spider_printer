#!/usr/bin/python3.7
from spider_printer import Spider

s = Spider()
pos = s.position
print(pos)
pos[2] *= 0.75
print(pos)
s.position = pos
print(pos)
