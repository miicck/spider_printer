#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np
import sys

route = []
with open(sys.argv[1]) as f:
    for line in f:
        point = [float(x) for x in line.split(",")]
        point.append(0)
        route.append(np.array(point))
route = np.array(route)

a = max(abs(route).flat)
route /= a
route *= float(input("Scale factor: "))

if input("Would you like to center the path? y/n: ") == "y":
    for i in range(2):
        route[:, i] -= (max(route[:,i]) + min(route[:, i]))*0.5

route = list(route)
route = [[0.0, 0.0, 0.0]] + route # Ensure we start at the origin
route = np.array(route)

for i in range(2):
    a, b = min(route[:, i]), max(route[:, i])
    print(f"{['x', 'y'][i]} range = [{a}, {b}]")

if input("Would you like to see the path now? y/n: ") == "y":
    import matplotlib.pyplot as plt
    plt.plot(route.T[0], route.T[1])
    plt.gca().set_aspect(1.0)
    plt.show()

s = Spider()

path_length = sum(np.linalg.norm(route[i]-route[i-1]) for i in range(1, len(route)))
eta = round(s.estimated_draw_time(path_length))

if input(f"Would you like to send the route to the printer? (ETA = {eta}s) y/n: ") == "y":
    for i in range(1, len(route)):
        dr = route[i] - route[i-1]
        s.move(dr)

    s.wait_done()

    if input("Would you like to reset the position now? y/n: ") == "y":
        s.move(-route[-1])

s.stop()
