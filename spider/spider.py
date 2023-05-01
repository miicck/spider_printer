from spider_printer.spider.fake_gpio import FakeGPIO

try:
    import RPi.GPIO as gpio
except ImportError:
    gpio = FakeGPIO()

import numpy as np
import time
from typing import Tuple, List

CM_TO_REV = 0.25
MM_PER_REV = 40
ALU_TRI_RADIUS = 554 / MM_PER_REV
LID_RADIUS = 1.35


def sphere_intersection_distance(c1: np.ndarray, r1: float, c2: np.ndarray, r2: float):
    # Returns distance from C1 along line connecting C1 and C2
    # at the plane continaing the intersection of the spheres
    c = np.linalg.norm(c1 - c2)

    if c < abs(r1 - r2):
        # One inside another - return line midway 
        # between on inside of the larger sphere
        if r1 > r2:
            return ((c + r2) + r1) / 2
        return -(r1 - c + r2) / 2

    # if c > r1 + r2:
    # No intersection - the below
    # result is still the best definition
    # as the bisection lines of three circles
    # cross at a single point
    return (r1 ** 2 - r2 ** 2 + c ** 2) / (2 * c)


class Spider:

    def __init__(self, pins=((2, 3), (17, 27), (10, 11)),
                 inner_radius=LID_RADIUS,
                 outer_radius=ALU_TRI_RADIUS,
                 auto_reset=True,
                 step_time=0.01,
                 gp=gpio,
                 initial_position=(0, 0, 0)):

        # Save input settings
        self._pins = pins
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._auto_reset = auto_reset
        self._gp = gp
        self._init_position = np.array(initial_position, dtype=float)

        # steps per full rotation
        self._steps_per_dl = 200

        # Time in seconds to make a single step
        # (much lower than 0.01 and something struggles
        #  to keep up with the pulse rate and the motors
        #  get confused about their direction)
        self._step_time = step_time

        # Setup motor pins
        self._gp.setmode(self._gp.BCM)
        for step_pin, dir_pin in self._pins:
            self._gp.setup(step_pin, self._gp.OUT)
            self._gp.setup(dir_pin, self._gp.OUT)

        # Work out the position of each motor/link point
        self._motor_positions = np.zeros((3, 3))
        for i, angle in enumerate([np.pi / 2 + np.pi / 3, np.pi / 2 - np.pi / 3, 3 * np.pi / 2]):
            self._motor_positions[i] = (np.cos(angle), np.sin(angle), 0.0)
        self._link_offsets = self._motor_positions.copy()
        self._motor_positions *= outer_radius
        self._link_offsets *= inner_radius

        # Number of steps each motor has taken
        self._steps = [0, 0, 0]

    def __del__(self):
        if self._auto_reset:
            self.position = np.zeros(3)

    @property
    def inner_radius(self) -> float:
        return self._inner_radius

    @property
    def outer_radius(self) -> float:
        return self._outer_radius

    @property
    def wire_lengths(self) -> np.ndarray:
        # Initial wire lengths +
        # Additional length due to steps
        return self.wire_lengths_at(self._init_position) + \
               np.array(self._steps) / self._steps_per_dl

    @property
    def position(self) -> np.ndarray:

        # Will contain return value
        pos = np.zeros(3)

        # Get reference positions (and their magnitudes)
        ref_poss = self._motor_positions - self._link_offsets
        ref_mags = np.linalg.norm(ref_poss, axis=1)
        assert all(abs(p[2]) < 1e-4 for p in ref_poss), \
            "This method assumes reference positions in the Z = 0 plane!"

        # Get lengths (distances of point to reference positions)
        ls = self.wire_lengths

        # Solve for x, y position (in each of the three possible ways)
        for pairs in [
            [[0, 1], [0, 2]],
            [[1, 0], [1, 2]],
            [[2, 0], [2, 1]]
        ]:
            m = np.zeros((2, 2))  # Matrix on LHS
            b = np.zeros(2)  # Vector on RHS
            for n, (i, j) in enumerate(pairs):
                m[n] = (ref_poss[i] - ref_poss[j])[:2]
                b[n] = (ref_mags[i] ** 2 - ref_mags[j] ** 2 + ls[j] ** 2 - ls[i] ** 2) / 2
            pos[:2] += np.linalg.solve(m, b)

        # Average the result
        pos[:2] /= 3.0

        # Solve for z
        zs = []
        for i in range(3):
            zs.append(2 * np.dot(pos, ref_poss[i]) + ls[i] ** 2 - ref_mags[i] ** 2 - np.linalg.norm(pos) ** 2)

        pos[2] = -abs(np.mean(zs)) ** 0.5

        return pos

    @position.setter
    def position(self, pos: np.ndarray):

        # Work out the new wire lengths
        wire_lengths = self.wire_lengths_at(pos)

        # Work out how many steps each motor needs to take to adjust the position
        delta_lengths = wire_lengths - self.wire_lengths
        steps = [round(x * self._steps_per_dl) for x in delta_lengths]
        abs_steps = [abs(s) for s in steps]
        max_steps = max(abs_steps)
        if max_steps == 0:
            return  # No full step to make

        # Work out a pattern for making the required steps
        step_freq = np.array(abs_steps) / max_steps
        cum_steps = np.zeros(3)
        step_pattern = [[False, False, False]]
        while True:

            tot_steps = np.sum(step_pattern, axis=0)
            if np.allclose(tot_steps, abs_steps):
                break  # Generated the correct number of steps

            # Work out which motors should make a step
            cum_steps += step_freq
            make_steps = cum_steps >= 1.0
            for i in range(3):
                if tot_steps[i] >= abs_steps[i]:
                    make_steps[i] = False

            step_pattern.append(make_steps)
            cum_steps -= step_pattern[-1]

        # Check the generated step pattern results in the correct number of steps
        total_steps = np.sum(step_pattern, axis=0)
        assert np.allclose(total_steps, abs_steps), f"{total_steps} != {abs_steps}"
        expected_steps_after = [self._steps[i] + steps[i] for i in range(3)]

        # Set the step directions
        for i, (step_pin, dir_pin) in enumerate(self._pins):
            self._gp.output(dir_pin, self._gp.HIGH if steps[i] >= 0 else self._gp.LOW)

        # Make the steps
        for p in step_pattern:

            if all([not x for x in p]):
                continue  # No steps in this part of the pattern

            # Reset to low (do this first, to give the dir pin
            # change maximum time to be regestered before the high pulse)
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                if p[i]:
                    self._gp.output(step_pin, self._gp.LOW)
            self.sleep(self._step_time / 2)

            # High edge of step pulse
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                if p[i]:
                    self._gp.output(step_pin, self._gp.HIGH)
                    self._steps[i] += 1 if steps[i] > 0 else -1  # Record step made
            self.sleep(self._step_time / 2)

        # Check the expected number of steps were made by each motor
        for i in range(3):
            assert expected_steps_after[i] == self._steps[i]

    def tension(self, amt: float, motors=(0, 1, 2)):

        # Work out how many steps this tensioning corresponds to
        steps = round(-amt * self._steps_per_dl)

        # Set the step directions
        for i in motors:
            self._gp.output(self._pins[i][1], self._gp.HIGH if steps >= 0 else self._gp.LOW)

        for n in range(abs(steps)):

            # Set step pins to low
            for i in motors:
                self._gp.output(self._pins[i][0], self._gp.LOW)
            self.sleep(self._step_time / 2)

            # High edge of step pulse
            for i in motors:
                self._gp.output(self._pins[i][0], self._gp.HIGH)
            self.sleep(self._step_time / 2)

    def sleep(self, sleep_time: float):
        if isinstance(self._gp, FakeGPIO):
            return
        time.sleep(sleep_time)

    def wire_lengths_at(self, pos: np.ndarray) -> np.array:
        # Work out the wire lengths at the given position
        wire_lengths = np.zeros(3)
        for i in range(3):
            mi = self._motor_positions[i]
            li = pos + self._link_offsets[i]
            wire_lengths[i] = np.linalg.norm(mi - li)
        return wire_lengths

    @property
    def motor_positions(self) -> np.ndarray:
        return self._motor_positions

    @property
    def link_positions(self) -> np.ndarray:
        return self.position + self._link_offsets

    @property
    def steps(self) -> List[int]:
        return list(self._steps)

    def draw(self):
        import matplotlib.pyplot as plt

        def plot_circle(c, r, **kwargs):
            plt.scatter([c[0]], [c[1]], **kwargs)
            xs = []
            ys = []
            for t in np.linspace(0, np.pi * 2, 100):
                xs.append(r * np.cos(t) + c[0])
                ys.append(r * np.sin(t) + c[1])
            plt.plot(xs, ys, **kwargs)

        colors = ["red", "green", "blue"]

        for i in range(3):
            # Draw motor
            mi = self._motor_positions[i]
            plt.scatter([mi[0]], [mi[1]], color=colors[i])

            # Draw motor circle
            plot_circle(mi, self.wire_lengths[i], color=colors[i], alpha=0.2)

            # Draw link
            li = self.link_positions[i]
            plt.scatter([li[0]], [li[1]], color=colors[i])

            # Draw wire with current wire length
            ni = (li - mi) / np.linalg.norm(li - mi)
            wi = ni * self.wire_lengths[i]
            plt.plot([mi[0], mi[0] + wi[0]], [mi[1], mi[1] + wi[1]], color=colors[i])

        # Draw inner/outer radii
        plot_circle(self.position, self._inner_radius, color="black")
        plot_circle(np.zeros(3), self._outer_radius, color="black")

        # Draw length indicators
        for i in range(3):
            y = -(self._outer_radius * (1 + (i + 1) * 0.1))
            plt.plot([0, self.wire_lengths[i]], [y, y], color=colors[i])

        plt.gca().set_aspect(1.0)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    s = Spider()
    plt.ion()
    plt.show()
    errors = []
    positions = []
    N = 100
    while True:
        for theta in np.linspace(0, 2 * np.pi, N):
            plt.clf()

            plt.subplot(221)
            pos = np.array([np.cos(theta), np.sin(theta), 0]) * s.outer_radius / 3
            plt.axvline(pos[0], color="black", alpha=0.1)
            plt.axhline(pos[1], color="black", alpha=0.1)
            s.position = pos
            s.draw()
            plt.xlim([-s.outer_radius * 2, s.outer_radius * 2])
            plt.ylim([-s.outer_radius * 2, s.outer_radius * 2])

            plt.subplot(222)
            errors.append(np.linalg.norm(pos - s.position) * MM_PER_REV)
            errors = errors[-N:]
            plt.plot(errors)

            plt.subplot(223)
            positions.append(s.position)
            positions = positions[-N:]
            plt.plot([p[0] for p in positions], [p[1] for p in positions])
            plt.gca().set_aspect(1.0)
            plt.xlim([-s.outer_radius, s.outer_radius])
            plt.ylim([-s.outer_radius, s.outer_radius])

            plt.pause(0.001)
