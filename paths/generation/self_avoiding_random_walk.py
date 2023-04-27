#!/usr/bin/python3
import numpy as np
import random
from plot_xy import plot
import sys

# Parameters
grid_size = int(sys.argv[1])
density = float(sys.argv[2])
self_inter_prob = 0.1
smooth = 0.5
edge_bias = 0.0
boundary = ["circle", "square"][0]

# Taken grid squares
grid = np.full((grid_size, grid_size), False)

if boundary == "circle":
    def in_range(x,y):
        r = grid_size // 2
        dx = x - r
        dy = y - r
        return dx*dx + dy*dy < r * r

if boundary == "square":
    def in_range(x,y):
        if x < 0: return False
        if y < 0: return False
        if x >= grid_size: return False
        if y >= grid_size: return False
        return True

def taken(x,y):
    if not in_range(x,y): return True
    return grid[x,y]

# Allowed moves/initial path point
moves = [[-1, 0], [1, 0], [0, 1], [0, -1]]
path = [[i//2 for i in grid.shape]]

while len(path) < grid.shape[0]*grid.shape[1]*density:

    xy = [[path[-1][0]+m[0], path[-1][1]+m[1]] for m in moves]
    free = [c for c in xy if not taken(*c)]

    if len(free) == 0:
        free = [c for c in xy if in_range(*c)]

    i = random.randint(0, len(free)-1)
    c = free[i]

    if edge_bias > 1e-5:
        if np.linalg.norm(np.array(c) - np.array(path[0])) < np.linalg.norm(np.array(path[-1]) - np.array(path[0])):
            if np.random.random() > 1-edge_bias:
                continue

    grid[c[0], c[1]] = True
    path.append(c)

path = np.array(path, dtype=float)

# smoothing
f = 1-smooth
for i in range(1, len(path)-1):
    path[i] = f*path[i]+(smooth/2)*path[i-1]+(smooth/2)*path[i+1]

with open("sarw.xy", "w") as f:
    for p in path:
        f.write(f"{p[0]}, {p[1]}\n")
plot("sarw.xy")
