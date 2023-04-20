try:
    import RPi.GPIO as gp
except ImportError:
    gp = None

import numpy as np
import time

CM_TO_REV = 0.25
ALU_TRI_RADIUS = CM_TO_REV*55.4

class Spider:

    def __init__(self, pins=((2,3), (17,27), (10, 11)),
                 inner_radius=0.0,
                 outer_radius=ALU_TRI_RADIUS):

        # Save input settings
        self._pins = pins
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius

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

        # Set initial position
        self._position = np.zeros(3)
        self._cum_dl = np.zeros(3)

        # Work out useful constants
        self._steps_per_dl = 200 # steps per full rotation
        self._step_time = 0.01 # Time in seconds to make a single step

        # Initial checks
        assert np.allclose(self.link_positions, self._link_offsets)

    def move(self, dx: np.ndarray):
        dx = np.array(dx)
        
        # Work out string lengths before move
        ls_before = np.linalg.norm(self._motor_positions - self.link_positions, axis=1)

        # Work out string lengths after move
        ls_after = np.linalg.norm(self._motor_positions - self.link_positions - dx, axis=1)
        
        # Add length changes to cumulative total
        self._cum_dl += ls_after - ls_before

        # Work out how many steps to take, subtract the
        # resulting length changes from the cumulative total
        steps = [round(float(x)) for x in self._cum_dl * self._steps_per_dl]
        self._cum_dl -= np.array(steps) / self._steps_per_dl
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

        # Set the step directions
        for i, (step_pin, dir_pin) in enumerate(self._pins):
            gp.output(dir_pin, gp.HIGH if steps[i] >= 0 else gp.LOW)

        # Make the steps 
        for p in step_pattern:

            # Interpolate position
            self._position += dx / len(step_pattern)

            if all([not x for x in p]):
                continue # No steps in this part of the pattern

            # High edge of step pulse
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                gp.output(step_pin, gp.HIGH if p[i] else gp.LOW)
            time.sleep(self._step_time/2)

            # Reset to low again
            for i, (step_pin, dir_pin) in enumerate(self._pins):
                gp.output(step_pin, gp.LOW)
            time.sleep(self._step_time/2)
    
    @property
    def link_positions(self) -> np.ndarray:
        return np.array([self._position + o for o in self._link_offsets])

    def __del__(self):

        # Reset position
        self.move(-self._position)

        # Clean up GPIO state
        gp.cleanup()

if __name__ == "__main__":
    import sys
    step_size = float(sys.argv[1])

    s = Spider()
    while True:
        for i in range(3):
            s.move(s._motor_positions[i]*step_size)
            s.move(-s._motor_positions[i]*step_size)
