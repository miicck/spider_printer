from typing import Tuple, Iterable
import numpy as np

class CrossHatchSquare:

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], lines: int):

        # Save settings
        self._start = start
        self._end = end
        self._path = None
        self._lines = max(lines, 2)

    @property
    def path(self) -> Iterable[Tuple[float, float]]:

        # Return existing path
        if self._path is not None:
            return self._path

        # Init location
        is_left = self._start[0] == 0
        is_up = self._start[1] == 1

        # Generate path
        self._path = []
        for i in range(self._lines):
            y = i / (self._lines-1)
            if is_up:
                y = 1.0 - y

            if is_left:
                self._path.extend([(0, y), (1, y)])
            else:
                self._path.extend([(1, y), (0, y)])

            is_left = not is_left

        is_up = not is_up

        if self._path[-1][1] > 0.5 and self._end[1] == 0:
            self._path.append((self._path[-1][0], 0))
        elif self._path[-1][1] < 0.5 and self._end[1] == 1:
            self._path.append((self._path[-1][0], 1))
            
        if self._path[-1][0] < 0.5 and self._end[0] == 1:
            self._path.append((1, self._path[-1][1]))
        elif self._path[-1][0] > 0.5 and self._end[0] == 0:
            self._path.append((0, self._path[-1][1]))

        self._path = np.array(self._path)
        return self._path


    def plot(self):
        import matplotlib.pyplot as plt
        CrossHatchSquare.plot_ch(self.path)
        plt.show()

    @staticmethod
    def plot_ch(path, offset=np.zeros(2)):
        import matplotlib.pyplot as plt
        path = np.array(path)
        path[:, 0] += offset[0]
        path[:, 1] += offset[1]
        plt.gca().set_aspect(1.0)
        for i in range(1, len(path)):
            plt.plot(path[i-1:i+1, 0], path[i-1:i+1, 1], color="black")
        plt.scatter(path[0:1, 0], path[0:1, 1], color="green")
        plt.scatter(path[-1:, 0], path[-1:, 1], color="red")

    @staticmethod
    def crosshatch_grid_path(grid: np.ndarray, plot=False):

        grid = np.asarray(grid)
        grid_path = []

        if plot:
            import matplotlib.pyplot as plt
            plt.figure()

        for y in range(grid.shape[1]):

            x_range = range(grid.shape[0]) if y % 2 == 0 else range(grid.shape[0]-1, -1, -1)
            x_range = list(x_range)

            for x in x_range:
                end   = [1, 0] if y % 2 == 0 else [0, 0]
                start = [0, 0] if y % 2 == 0 else [1, 0]

                if x == x_range[-1]:
                    # End of row
                    end[1] = 1

                c = CrossHatchSquare(start=start, end=end, lines=int(grid[x,y]))

                c_path = np.array(c.path)
                c_path[:, 0] += x
                c_path[:, 1] += y
                grid_path.extend(c_path)

                if plot:
                    CrossHatchSquare.plot_ch(c.path, offset=(x*1.1,y*1.1))

        grid_path = np.array(grid_path)

        if plot:
            plt.figure()
            for i in range(1, len(grid_path)):
                plt.plot(grid_path[i-1:i+1, 0], grid_path[i-1:i+1, 1], color="black")

        return grid_path

def image_to_crosshatch_path(image: str, plot=False, downsampling: int = 1, max_hatch=10, save_as:str="img2cross.xy", rotate90=False):
    import imageio.v3 as iio
    import numpy as np

    im = iio.imread(image)
    im = np.mean(im, axis=-1)
    im /= max(im.flat)
    im = im[::downsampling, ::downsampling]

    if rotate90:
        im = im.T

    path = CrossHatchSquare.crosshatch_grid_path((1.0-im)*max_hatch)

    with open(save_as, "w") as f:
        for p in path:
            f.write(f"{p[0]}, {p[1]}\n")
    print("Image saved as "+save_as)

    if plot:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(-im, cmap="Greys")

        plt.figure()
        plt.gca().set_aspect(1.0)
        for i in range(1, len(path)):
            plt.plot(path[i-1:i+1, 0], path[i-1:i+1, 1], color="black")

        plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    CrossHatchSquare.crosshatch_grid_path(np.random.random((4,4))*10, plot=True)
    plt.show()
