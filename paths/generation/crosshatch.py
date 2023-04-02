from typing import Tuple, Iterable
import numpy as np

class CrossHatchSquare:

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int], lines: int):

        # Save settings
        self._start = start
        self._end = end
        self._path = None
        self._lines = lines

    @property
    def path(self) -> Iterable[Tuple[float, float]]:

        # Return existing path
        if self._path is not None:
            return self._path

        # Init location
        is_left = self._start[0] == 0
        is_up = self._start[0] == 1

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

        self._path = np.array(self._path)
        return self._path


    def plot(self):
        import matplotlib.pyplot as plt

        for i in range(1, len(self.path)):
            plt.plot(self.path[i-1:i+1, 0], self.path[i-1:i+1, 1], color="black")

        plt.show()

if __name__ == "__main__":
    
    c = CrossHatchSquare(start=(0,0), end=(1,0), lines=20)
    c.plot()
