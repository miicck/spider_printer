try:
    import RPi.GPIO as gp
except ImportError:
    from fake_gpio import gp

import numpy as np
import time
from typing import Tuple

CM_TO_REV = 0.25
MM_PER_REV = 40
ALU_TRI_RADIUS = 554/MM_PER_REV
LID_RADIUS = 1.35

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

class Spider:
    
    def __init__(self, pins=((2,3), (17,27), (10, 11)),
                 inner_radius=LID_RADIUS,
                 outer_radius=ALU_TRI_RADIUS,
                 auto_reset=True):

        # Save input settings
        self._pins = pins
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._auto_reset = auto_reset
        print(self._outer_radius)

        # steps per full rotation
        self._steps_per_dl = 200

        # Time in seconds to make a single step
        # (much lower than 0.01 and something struggles
        #  to keep up with the pulse rate and the motors
        #  get confused about their direction)
        self._step_time = 0.01

        # Setup motor pins
        gp.setmode(gp.BCM)
        for step_pin, dir_pin in self._pins:
            gp.setup(step_pin, gp.OUT)
            gp.setup(dir_pin, gp.OUT)

        # Work out the position of each motor/link point
        self._motor_positions = np.zeros((3,3))
        for i, angle in enumerate([np.pi/2+np.pi/3, np.pi/2-np.pi/3, 3*np.pi/2]):
            self._motor_positions[i] = (np.cos(angle), np.sin(angle), 0.0)
        self._link_offsets = self._motor_positions.copy()
        self._motor_positions *= outer_radius
        self._link_offsets *= inner_radius

        # Number of steps each motor has taken
        self._steps = [0, 0, 0]

    @property
    def inner_radius(self) -> float:
        return self._inner_radius

    @property
    def outer_radius(self) -> float:
        return self._outer_radius

    @property
    def lengths(self) -> np.ndarray:

        # Initial length of strings
        l0 = self._outer_radius - self._inner_radius

        # Add additional length due to steps
        return l0 + np.array(self._steps) / self._steps_per_dl

    @property
    def position(self) -> np.ndarray:

        def intersection_plane(i: int, j: int) -> Tuple[np.ndarray, np.ndarray]:
            # Returns point and normal of intersection plane
            # of length spheres for motors i and j, offset so
            # their link points coincide
            ci, cj = (self._motor_positions - self._link_offsets)[[i,j]]
            li, lj = self.lengths[[i,j]]
            dij = sphere_intersection_distance(ci, li, cj, lj) 
            nij = (cj - ci) / np.linalg.norm(cj - ci)
            pij = ci + nij*dij
            return pij, nij

        # Three intersection planes
        p1, n1 = intersection_plane(0, 1)
        p2, n2 = intersection_plane(1, 2)
        p3, n3 = intersection_plane(0, 2)

        # Get a vector in plane 1 with non-zero projection onto n2
        t1 = n2 - np.dot(n2, n1)*n1
        t1 /= np.linalg.norm(t1)
        assert np.allclose(np.dot(t1, n1), 0) # t1 lies in plane 1
        assert abs(np.dot(t1, n2)) > 1e-5 # non-zero projection onto n2

        # Get a point in both plane 1 and 2
        mu = np.dot(p2-p1, n2) / np.dot(t1, n2)
        r12 = p1 + mu * t1
        assert np.allclose(np.dot(r12 - p1, n1), 0), np.dot(r12 - p1, n1)
        assert np.allclose(np.dot(r12 - p2, n2), 0), np.dot(r12 - p2, n2)

        # Get vector along intersection line of planes 1 and 2
        t12 = np.cross(n1, n2)
        t12 /= np.linalg.norm(t12)

        # Get intersection point of all three planes
        if np.allclose(np.dot(r12 - p3, n3), 0):
            pos = r12 # r12 already in plane 3
        else:
            lam = np.dot(r12 - p3, n3)/np.dot(t12, n3)
            pos = r12 + lam*t12

        # Check return point is in all three planes
        assert np.allclose(np.dot(pos - p1, n1), 0), np.dot(pos - p1, n1)
        assert np.allclose(np.dot(pos - p2, n2), 0)
        assert np.allclose(np.dot(pos - p3, n3), 0)

        return pos

    @position.setter
    def position(self, pos: np.ndarray):
        
        # Work out the new wire lengths
        wire_lengths = np.zeros(3)
        for i in range(3):
            mi = self._motor_positions[i]
            li = pos + self._link_offsets[i]
            wire_lengths[i] = np.linalg.norm(mi-li)

        # Work out how many steps each motor needs to take to adjust the position
        delta_lengths = wire_lengths - self.lengths
        steps = [round(x*self._steps_per_dl) for x in delta_lengths]
        abs_steps = [abs(s) for s in steps]
        max_steps = max(abs_steps)
        if max_steps == 0:
            return # No full step to make

        # Work out a pattern for making the required steps
        step_freq = np.array(abs_steps) / max_steps
        cum_steps = np.zeros(3)
        step_pattern = [[False, False, False]]
        while True:

            tot_steps = np.sum(step_pattern, axis=0)
            if np.allclose(tot_steps, abs_steps):
                break # Generated the correct number of steps

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
            gp.output(dir_pin, gp.HIGH if steps[i] >= 0 else gp.LOW)

        # Make the steps
        for p in step_pattern:

            if all([not x for x in p]):
                continue # No steps in this part of the pattern

            # Reset to low (do this first, to give the dir pin
            # change maximum time to be regestered before the high pulse)
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                if p[i]:
                    gp.output(step_pin, gp.LOW)
            time.sleep(self._step_time/2)

            # High edge of step pulse
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                if p[i]:
                    gp.output(step_pin, gp.HIGH)
                    self._steps[i] += 1 if steps[i] > 0 else -1 # Record step made
            time.sleep(self._step_time/2)

        # Check the expected number of steps were made by each motor
        for i in range(3):
            assert expected_steps_after[i] == self._steps[i]

    @property
    def motor_positions(self) -> np.ndarray:
        return self._motor_positions

    @property
    def link_positions(self) -> np.ndarray:
        return self.position + self._link_offsets

    def draw(self):
        import matplotlib.pyplot as plt

        def plot_circle(c, r, **kwargs):
            plt.scatter([c[0]], [c[1]], **kwargs)
            xs = []
            ys = []
            for t in np.linspace(0, np.pi*2, 100):
                xs.append(r*np.cos(t)+c[0])
                ys.append(r*np.sin(t)+c[1])
            plt.plot(xs, ys, **kwargs)
        
        colors = ["red", "green", "blue"]

        for i in range(3):

            # Draw motor
            mi = self._motor_positions[i]
            plt.scatter([mi[0]], [mi[1]], color=colors[i])

            # Draw motor circle
            plot_circle(mi, self.lengths[i], color=colors[i], alpha=0.2)

            # Draw link
            li = self.link_positions[i]
            plt.scatter([li[0]], [li[1]], color=colors[i])

            # Draw wire with current wire length
            ni = (li-mi)/np.linalg.norm(li-mi)
            wi = ni*self.lengths[i]
            plt.plot([mi[0], mi[0]+wi[0]], [mi[1], mi[1]+wi[1]], color=colors[i])

        # Draw inner/outer radii
        plot_circle(self.position, self._inner_radius, color="black")
        plot_circle(np.zeros(3), self._outer_radius, color="black")

        # Draw length indicators
        for i in range(3):
            y = -(self._outer_radius * (1 + (i+1)*0.1))
            plt.plot([0, self.lengths[i]], [y, y], color=colors[i])

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
        for theta in np.linspace(0, 2*np.pi, N):
            plt.clf()

            plt.subplot(221)
            pos = np.array([np.cos(theta), np.sin(theta), 0]) * s.outer_radius/3
            plt.axvline(pos[0], color="black", alpha=0.1)
            plt.axhline(pos[1], color="black", alpha=0.1)
            s.position = pos
            s.draw()
            plt.xlim([-s.outer_radius*2, s.outer_radius*2])
            plt.ylim([-s.outer_radius*2, s.outer_radius*2])

            plt.subplot(222)
            errors.append(np.linalg.norm(pos - s.position)*MM_PER_REV)
            errors = errors[-N:]
            plt.plot(errors)

            plt.subplot(223)
            positions.append(s.position)
            positions = positions[-N:]
            plt.plot([p[0] for p in positions], [p[1] for p in positions])
            plt.gca().set_aspect(1.0)
            plt.xlim([-s.outer_radius,s. outer_radius])
            plt.ylim([-s.outer_radius,s. outer_radius])

            plt.pause(0.001)
