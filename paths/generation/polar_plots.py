#!/usr/bin/python3
import numpy as np
import random
import sys
from plot_xy import plot

def conv_theta(theta: str) -> float:
    inp = theta
    if "pi" in inp:
        return float(inp.replace("pi", ""))*np.pi
    return float(inp)

def get_theta(msg: str) -> float:
    return conv_theta(input(msg))

def mandelbrot_iters(z):
    v = 0.0
    for n in range(100):
        v = v**2 + z
        if abs(v) > 2:
            return n
    return n

if len(sys.argv) < 4:
    print("Arguments: min theta, max theta, pattern letter")
    quit()


#min_theta = get_theta("Theta min: ")
#max_theta = get_theta("Theta max: ")
min_theta, max_theta = conv_theta(sys.argv[1]), conv_theta(sys.argv[2])
if len(sys.argv) > 4:
    steps = int(sys.argv[4])
else:
    steps = round(200 * (max_theta - min_theta) / 2*np.pi)
theta = np.linspace(min_theta, max_theta, steps)

if sys.argv[3] == "a":
    r = theta % 0.8
elif sys.argv[3] == "b":
    r = 4*np.cos(10.0*np.cos(theta))
elif sys.argv[3] == "c":
    r = 4*np.cos(2.3*theta)
elif sys.argv[3] == "d":
    r = 0.4*theta + np.sin(np.floor(np.exp(0.3*theta)))
elif sys.argv[3] == "e":
    r = theta + np.pi*2*np.sin(np.pi*theta*1.1)
elif sys.argv[3] == "f":
    # Recommended range (0, 39.2pi)
    r = theta + np.pi*2*np.sin(np.pi*theta)
elif sys.argv[3] == "g":
    # range (0, 20.5pi)
    z = np.cos(theta) + 1.0j*np.sin(theta)
    r = [np.log(mandelbrot_iters(x)) for x in z]
    r *= theta * 4


x = np.cos(theta)*r
y = np.sin(theta)*r

with open("polar.xy", "w") as f:
    for x, y in zip(x,y):
        f.write(f"{x}, {y}\n")
plot("polar.xy")
