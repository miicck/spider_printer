#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np
import sys

route = []
with open(sys.argv[1]) as f:
    for line in f:
        route.append([float(x) for x in line.split(",")] + [0.0])
route = np.array(route)

# Normalize route so maximum of width, height
# is given by the scale factor
a = 0.0
for i in range(2):
    a = max(a, max(route[:, i]) - min(route[:,i]))
route /= a
route *= float(input("Scale factor: "))

if input("Would you like to center the path? y/n: ") == "y":
    # Center the path
    for i in range(2):
        route[:, i] -= (max(route[:,i]) + min(route[:, i]))*0.5

# Ensure we start at the origin
route = list(route)
route = [[0.0, 0.0, 0.0]] + route 
route = np.array(route)

# Print range in each coordinate
for i in range(2):
    a, b = min(route[:, i]), max(route[:, i])
    print(f"{['x', 'y'][i]} range = [{a}, {b}]")

if input("Would you like to see the path now? y/n: ") == "y":
    # Plot path
    import matplotlib.pyplot as plt
    plt.plot(route.T[0], route.T[1])
    plt.gca().set_aspect(1.0)
    plt.show()

if input(f"Would you like to send the route to the printer? y/n: ") == "y":
    # Draw path
    s = Spider()
    for i in range(1, len(route)):
        dr = route[i] - route[i-1]
        s.move(dr)
