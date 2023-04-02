#!/usr/bin/python3.7
import matplotlib.pyplot as plt
import numpy as np
import random

path = [[0,0]]

max_d = 20
hits = [False]*4

while True:
    
    x, y = path[-1]
    x += random.randint(-1,1)
    y += random.randint(-1,1)

    if x >  max_d: 
        x = max_d
        hits[0] = True
    if x < -max_d: 
        x = -max_d
        hits[1] = True
    if y >  max_d: 
        y = max_d
        hits[2] = True
    if y < -max_d: 
        y = -max_d
        hits[3] = True

    path.append([x,y])

    if x == 0 and y == 0 and all(hits):
        break

path = np.array(path, dtype=float)
path /= max_d
plt.plot(path.T[0], path.T[1])
plt.gca().set_aspect(1.0)

with open("rw", "w") as f:
    for p in path:
        f.write(f"{p[0]}, {p[1]}\n")

plt.show()
