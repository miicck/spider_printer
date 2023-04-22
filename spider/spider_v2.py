try:
    import RPi.GPIO as gp
except ImportError:
    gp = None

import numpy as np
import time

def sphere_intersection_distance(c1: np.ndarray, r1: float, c2: np.ndarray, r2: float):
    # Returns distance from C1 along line connecting C1 and C2
    # at the plane continaing the intersection of the spheres
    c = np.linalg.norm(c1 - c2)

    if c < abs(r1-r2):
        # One inside another - return line midway 
        # between on inside of the larger sphere
        if r1 > r2:
            return ((c + r2) + r1)/2
        return -(r1-c + r2)/2

    # if c > r1 + r2:
    # No intersection - the below
    # result is still the best definition
    # as the bisection lines of three circles
    # cross at a single point
    return (r1**2 - r2**2 + c**2)/(2*c)




if __name__ == "__main__":
    import matplotlib.pyplot as plt

    def plot_circle(c, r):
        plt.scatter([c[0]], [c[1]], color="black")
        xs = []
        ys = []
        for t in np.linspace(0, np.pi*2, 1024):
            xs.append(r*np.cos(t)+c[0])
            ys.append(r*np.sin(t)+c[1])
        plt.plot(xs, ys, color="black")

    def plot_intersection(c1, r1, c2, r2):
        n = (c2 - c1) / np.linalg.norm(c2 - c1)
        a = sphere_intersection_distance(c1, r1, c2, r2)*n + c1
        t = np.array([n[1], -n[0]])
        plt.scatter([a[0]], [a[1]])
        plt.plot([a[0]+t[0], a[0]-t[0]], [a[1]+t[1], a[1]-t[1]])
        plt.gca().set_aspect(1.0)

    for y in [0, 4, 8, 12, 16, 20, 24, 28, 32]:

        # Plot circles
        c1 = np.array([0.0,y,0.0])
        r1 = 1.0
        c2 = np.array([y/16,y,0.0])
        r2 = 1.5
        plot_circle(c1, r1)
        plot_circle(c2, r2)

        # Plot intersection line
        plot_intersection(c1, r1, c2, r2)

    plt.figure()
    
    h = (3**(1/2))/2
    cs = np.array([[0,0,0], [1,0,0], [0.5,h,0.0]])
    rs = np.array([h/1.5,h/1.5,h/1.5])
    for i in range(3):
        plot_circle(cs[i], rs[i])

        for j in range(i):
            plot_intersection(cs[i], rs[i], cs[j], rs[j])

    plt.show()
