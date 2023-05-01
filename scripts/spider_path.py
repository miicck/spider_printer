#!/usr/bin/python3.7
from spider_printer import Spider
import numpy as np
import sys
import time

route = []
with open(sys.argv[1]) as f:
    for line in f:
        route.append([float(x) for x in line.split(",")] + [0.0])
route = np.array(route)
route -= route[0] # Start at origin

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

s = Spider()

path_length = sum(np.linalg.norm(route[i]-route[i-1]) for i in range(1, len(route)))
print(f"ETA: {s.seconds_per_dl*path_length}s")

if input(f"Would you like to send the route to the printer? y/n: ") == "y":
    # Draw path
    start_time = time.time()
    for i, r in enumerate(route):
        s.position = r
        x = (i+1)/len(route)
        t = time.time() - start_time
        print(f"{t:5.3f}s {x*100:5.3f}% complete, ETA = {t*(1-x)/x:10.5f}s")
