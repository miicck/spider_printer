#!/usr/bin/python3.7
from spider_printer import Spider
    
spider = Spider(auto_reset=False, step_time=0.005)
last_cmd = "w"
step_size = 0.01

while True:
    cmd = input().strip()
    if cmd != "":
        if len(cmd.split()) == 3:
            spider.position = [float(x) for x in cmd.split()]
        elif len(cmd.split()) > 1:
            last_cmd, amt = cmd.split()
            step_size = float(amt)
        else:
            last_cmd = cmd

    if last_cmd == "w":
        spider.position += (0,  step_size, 0)
    if last_cmd == "s":
        spider.position += (0, -step_size, 0)
    if last_cmd == "a":
        spider.position += (-step_size, 0, 0)
    if last_cmd == "d":
        spider.position += (step_size, 0, 0)
    if last_cmd == "e":
        spider.position += (0,0,step_size)
    if last_cmd == "q":
        spider.position += (0,0,-step_size)
    if last_cmd == "t":
        spider.tension(step_size)
    if last_cmd == "l":
        spider.tension(-step_size)
    if last_cmd == "ta":
        spider.tension(step_size, motors=[0])
    if last_cmd == "tb":
        spider.tension(step_size, motors=[1])
    if last_cmd == "tc":
        spider.tension(step_size, motors=[2])
    if last_cmd == "la":
        spider.tension(-step_size, motors=[0])
    if last_cmd == "lb":
        spider.tension(-step_size, motors=[1])
    if last_cmd == "lc":
        spider.tension(-step_size, motors=[2])

    print(spider.position)
