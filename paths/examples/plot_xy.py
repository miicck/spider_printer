import matplotlib.pyplot as plt
import numpy as np
import sys

path = []
with open(sys.argv[1]) as f:
    for line in f:
        path.append([float(x) for x in line.split(",")])

path = np.array(path)
plt.plot(path[:, 0], path[:, 1], color="black")
plt.show()
