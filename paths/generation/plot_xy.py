import matplotlib.pyplot as plt
import sys

def plot(fname):

    data = []
    with open(fname) as f:
        for line in f:
            data.append([float(x) for x in line.split(",")])

    x, y = zip(*data)
    plt.plot(x,y,color="black")
    plt.gca().set_aspect(1.0)
    plt.show()

if __name__ == "__main__":
    plot(sys.argv[1])
