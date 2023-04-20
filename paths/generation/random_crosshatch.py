from spider_printer.paths.generation.crosshatch import CrossHatchSquare
import sys
import numpy as np

size = int(input("Size (integer): "))
max_hatch = int(input("Max hatch (integer): "))

path = CrossHatchSquare.crosshatch_grid_path(np.random.random((size, size))*max_hatch)
with open("rand_crosshatch.xy", "w") as f:
    for p in path:
        f.write(f"{p[0]}, {p[1]}\n")
