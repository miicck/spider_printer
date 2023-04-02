#!/usr/bin/python3.7
from spider_printer import Spider
    
spider = Spider()
last_cmd = "w"
step_size = 0.01

while True:
    cmd = input().strip()
    if cmd != "":
        if len(cmd.split()) > 1:
            last_cmd, amt = cmd.split()
            step_size = float(amt)
        else:
            last_cmd = cmd

    if last_cmd == "w":
        spider.move((0,  step_size, 0))
    if last_cmd == "s":
        spider.move((0, -step_size, 0))
    if last_cmd == "a":
        spider.move((-step_size, 0, 0))
    if last_cmd == "d":
        spider.move(( step_size, 0, 0))
    if last_cmd == "e":
        spider.move((0,0,step_size))
    if last_cmd == "q":
        spider.move((0,0,-step_size))
