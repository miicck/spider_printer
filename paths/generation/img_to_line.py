import imageio.v3 as iio
import random
import matplotlib.pyplot as plt
import numpy as np
import sys

im = iio.imread(sys.argv[1])
im = np.mean(im, axis=-1)
im /= max(im.flat)
im = 1-im

# Increase contrast
im = im ** float(sys.argv[2])

route = [(im.shape[0]//2, im.shape[1]//2)]

iterations = 10000
max_step = max(im.shape) // 30

while len(route) < iterations:

    #move = (random.randint(-1, 1)*max_step, random.randint(-1, 1)*max_step)
    #move = (random.randint(-2, 2)*max_step//2, random.randint(-2, 2)*max_step//2)
    #move = [round(max_step*x) for x in (np.random.random(2) - 0.5)*2]
    move = (random.randint(-max_step, max_step), random.randint(-max_step, max_step))

    new = (route[-1][0] + move[0], route[-1][1] + move[1])

    new = (
    min(max(new[0], 0), im.shape[0]-1),
    min(max(new[1], 0), im.shape[1]-1)
    )

    p_accept = im[new] / im[route[-1]]

    if p_accept > np.random.random():
        route.append(new)

with open("image_line.xy", "w") as f:
    for r in route:
        f.write(f"{r[0]}, {r[1]}\n")

ys, xs = np.array(route).T
ys = [im.shape[0] - y - 1 for y in ys]

plt.imshow(im, cmap="Greys")

plt.figure()
for i in range(1, len(xs)):
    plt.plot(xs[i-1:i+1], ys[i-1:i+1], color="black", alpha=0.1)
plt.gca().set_aspect(1.0)

plt.show()
