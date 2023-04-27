#!/usr/bin/python3
import numpy as np
import random
from plot_xy import plot

def mandel_iter(z):
    f = 0.0
    for n in range(100):
        f = f**2 + z
        if abs(f) > 2.0:
            return n
    return n

path = [0.15 - 0.6j]

x = path[-1]

STEP_SIZE = 0.01
RESCALE = 1 + STEP_SIZE
ROTATE = STEP_SIZE

dx = STEP_SIZE

for n in range(10000):
    #x += (np.random.random()*-0.5)*2*STEP_SIZE
    #x += (np.random.random()*-0.5)*2*STEP_SIZE*1.0j

    x += dx
    dx *= np.exp(ROTATE*40.0j)

    if mandel_iter(x) > 50:
        x *= RESCALE
    else:
        x /= RESCALE

    #x *= np.exp(ROTATE*1.0j)
    path.append(x)

path = np.array([[x.real, x.imag] for x in path])
with open("mandel_walk.xy", "w") as f:
    for p in path:
        f.write(f"{p[0]}, {p[1]}\n")
plot("mandel_walk.xy")
