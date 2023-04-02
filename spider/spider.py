try:
    import RPi.GPIO as gp
except ImportError as e:
    gp = None
import numpy as np
import threading
import queue
import time

CM_TO_REV = 0.25

LID_RADIUS = 5.25*CM_TO_REV
CARD_TRI_RADIUS = 50.0*CM_TO_REV

class Spider:

    def __del__(self):
        gp.cleanup()

    def estimated_draw_time(self, path_length: float) -> float:
        return path_length*self._steps_per_dl*self._step_time

    def __init__(self, pins=((2,3), (17,27), (10,11)), outer_radius=CARD_TRI_RADIUS, inner_radius=0.0):

        # Step delay
        #self._step_time = 0.0005
        self._step_time = 0.01

        # Save stepper motor pins
        self._pins = pins

        # Setup pins
        gp.setmode(gp.BCM)
        for step_pin, dir_pin in self._pins:
            gp.setup(step_pin, gp.OUT)
            gp.setup(dir_pin,  gp.OUT)

        # We work in units of legnth corresponding to a single rotation of a stepper motor
        self._microstepping = 1
        self._steps_per_dl = 200 * self._microstepping

        # Work out the position of each motor/link point
        self._motor_positions = np.zeros((3,3))
        for i, angle in enumerate([np.pi/2+np.pi/3, np.pi/2-np.pi/3, 3*np.pi/2]):
            self._motor_positions[i] = (np.cos(angle), np.sin(angle), 0.0)
        self._link_offsets = self._motor_positions.copy()
        self._motor_positions *= outer_radius
        self._link_offsets *= inner_radius

        # Setup the move queue
        self._move_queue = queue.Queue()
        self._all_moves = []

        def control_loop():
            
            # Cumulative change in lengths
            cum_dl = np.zeros(3)
            position = np.zeros(3)

            while True:

                # Work out change in line vectors
                next_dr = self._move_queue.get()
                if next_dr is None:
                    break # Stop

                l_from = self.lines(position)
                l_to = self.lines(position+next_dr)
                position += next_dr
                
                # Add change in lengths to cumulative total
                for i in range(3):
                    dl = np.linalg.norm(l_to[i]) - np.linalg.norm(l_from[i])
                    cum_dl[i] += dl

                # Get as close as we can to the current cumulative 
                # length change using an integer number of steps
                steps = np.array([round(cum_dl[i]*self._steps_per_dl) for i in range(3)], dtype=int)
                cum_dl -= steps/self._steps_per_dl

                # Total number of steps to make for each motor
                count_steps = abs(steps)

                # How often to make a step for each motor
                max_steps = max(abs(steps))
                step_freq = abs(steps)/max_steps if max_steps > 0 else np.zeros(3)

                # Progress towards next step for each motor
                cum_steps = np.zeros(3)

                qsize = self._move_queue.qsize()
                print(f"steps remaining: {qsize:<10}", end="\r", flush=True)

                while any(count_steps > 0):

                    # Accumulate step
                    cum_steps   += step_freq

                    # Make accumulated steps
                    make_step    = np.logical_and(cum_steps > 1.0, count_steps > 0)
                    count_steps -= make_step
                    cum_steps   -= make_step
                    
                    # Setup direction and start step pulse
                    for i, (step_pin, dir_pin) in enumerate(self._pins):
                        gp.output(dir_pin, gp.HIGH if steps[i] > 0 else gp.LOW)
                        gp.output(step_pin, gp.HIGH if make_step[i] else gp.LOW)

                    time.sleep(self._step_time/2)

                    # Stop step pulse
                    for i, (step_pin, dir_pin) in enumerate(self._pins):
                        gp.output(step_pin, gp.LOW)

                    time.sleep(self._step_time/2)

            
        self._control_thread = threading.Thread(target=control_loop)
        self._control_thread.start()

    def lines(self, r: np.ndarray):
        
        # Work out the spider line vectors for a given position r
        rmat = np.zeros((3,3))
        for i in range(3):
            rmat[i, :] = r
        return self._motor_positions - self._link_offsets - rmat

    def move(self, dr: np.ndarray):

        # Copy/cast
        dr = np.array(dr, dtype=float)
        
        # Add to the move queue
        self._move_queue.put(dr.copy())
        self._all_moves.append(dr.copy())

    def wait_done(self):
        while self._move_queue.qsize() > 0:
            time.sleep(0.2)

    def stop(self):
        self._move_queue.put(None)
        self._control_thread.join()

    def plot(self):
        import matplotlib.pyplot as plt

        plt.scatter(self._motor_positions[:, 0], self._motor_positions[:, 1], color="black")
        for i in range(3):
            plt.annotate(["A", "B", "C"][i], self._motor_positions[i, :2])

        positions = [np.zeros(3)]
        for dr in self._all_moves:
            positions.append(positions[-1]+dr)

        for i, r in enumerate(positions):

            lines = self.lines(r)
            alpha = np.exp(-i)

            for j in range(3):
                a = r + self._link_offsets[j]
                b = r + self._link_offsets[j] + lines[j]
                plt.plot((a[0], b[0]), (a[1], b[1]), color="green", alpha=alpha)
                plt.plot((r[0], a[0]), (r[1], a[1]), color="red", alpha=alpha)

        plt.gca().set_aspect(1.0)
        plt.show()

if __name__ == "__main__":

    import sys
    dx = float(sys.argv[1])
    dy = float(sys.argv[2])
    dz = 0

    if len(sys.argv) > 3:
        dz = float(sys.argv[3])

    s = Spider()
    while True:
        s.move((dx,dy,dz))
        input()
