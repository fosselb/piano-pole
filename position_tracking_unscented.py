import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
from serial import Serial, SerialException
from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints
from filterpy.common import Q_discrete_white_noise
from scipy.spatial.transform import Rotation
from scipy.linalg import block_diag, sqrtm


class CSV_Reader:
    def __init__(self, filename):
        with open(filename, "r") as file:
            contents = file.readlines()
            self.lines = iter(contents)

    def readline(self):
        return next(self.lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Track the position of an IMU.")
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument("-p", "--port", default="COM6", help="Serial port to listen to")
    exclusive.add_argument("-i", "--input", help="CSV file to read from")
    parser.add_argument("-o", "--output", help="CSV file to write to")
    return parser.parse_args()

def get_input(args):
    if args.input == None:
        try:
            source = Serial(args.port, 115200, timeout=10)
        except SerialException:
            sys.exit("Port '" + args.port + "' not available")
        for _ in range(100):
            source.readline()
    else:
        try:
            source = CSV_Reader(args.input)
        except FileNotFoundError:
            sys.exit("Input file '" + args.input + "' not found")
    return source

def get_output(args):
    if args.output == None:
        return None
    else:
        try:
            return open(args.output, "w")
        except:
            sys.exit("Unable to create output file '" + args.output + "'")

def get_next_reading(input, output):
    line = input.readline()
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    if output:
        output.write(line)
    line = line.strip()
    if line.endswith(","):
        line = line[:-1]
    data = np.array(list(map(float, line.split(","))))

    t_k = data[0]
    acc_k = data[1:5]
    quat_k = data[5:11]
    stability_k = data[11]

    accr_k = Rotation.from_quat(quat_k[0:4]).apply(acc_k[0:3])

    return t_k, accr_k, acc_k, quat_k, stability_k


if __name__ == "__main__":
    args = parse_args()
    input = get_input(args)
    output = get_output(args)

    points = MerweScaledSigmaPoints(n=9, alpha=0.01, beta=2, kappa=3-9, sqrt_method=sqrtm)
    def h(x):
        H_block = np.array([0, 0, 1])
        H = block_diag(H_block, H_block, H_block)
        return H @ x
    kalman = UnscentedKalmanFilter(dim_x=9, dim_z=3, dt=None, hx=h, fx=None, points=points)
    kalman.P = np.diag([0, 0, 20, 0, 0, 20, 0, 0, 20])
    kalman.R = np.diag([0.5, 0.5, 0.5])

    t_k, accr_k, acc_k, quat_k, stability_k = get_next_reading(input, output)

    t = np.array([t_k])
    posr = np.zeros((1, 3))
    velr = np.zeros((1, 3))
    accr = np.array([accr_k])

    kalman.x = np.hstack((posr[-1], velr[-1], accr[-1])).reshape(-1)

    try:
        while True:
            t_k, accr_k, acc_k, quat_k, stability_k = get_next_reading(input, output)

            t = np.append(t, t_k)
            dt = t[-1] - t[-2]

            def f(x, dt):
                if stability_k == 4:
                    F_block = np.array([[1, dt, dt**2/2], [0, 1, dt], [0, 0, 1]])
                else:
                    F_block = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
                F = block_diag(F_block, F_block, F_block)
                return F @ x
            Q_block = Q_discrete_white_noise(dim=3, dt=dt, var=1)
            kalman.Q = block_diag(Q_block, Q_block, Q_block)

            kalman.predict(dt=dt, fx=f)
            kalman.update(accr_k)

            x_k = kalman.x.reshape((3, 3), order="F")
            posr = np.vstack((posr, x_k[0]))
            velr = np.vstack((velr, x_k[1]))
            accr = np.vstack((accr, x_k[2]))

    except (StopIteration, KeyboardInterrupt):
        fig = plt.figure()
        # acc_ax = fig.add_subplot(3, 1, 1, projection="3d")
        # acc_ax.set_title("Acceleration Data from BNO085")
        # acc_ax.set_xlabel("X (m/s^2)")
        # acc_ax.set_ylabel("Y (m/s^2)")
        # acc_ax.set_zlabel("Z (m/s^2)")
        # acc_sc = acc_ax.scatter(accr[:,0], accr[:,1], accr[:,2], c=t-t.flat[0])
        # fig.colorbar(acc_sc, ax=acc_ax)
        # vel_ax = fig.add_subplot(3, 1, 2, projection="3d")
        # vel_ax.set_title("Velocity Data from BNO085")
        # vel_ax.set_xlabel("X (m/s)")
        # vel_ax.set_ylabel("Y (m/s)")
        # vel_ax.set_zlabel("Z (m/s)")
        # vel_sc = vel_ax.scatter(velr[:,0], velr[:,1], velr[:,2], c=t-t.flat[0])
        # fig.colorbar(vel_sc, ax=vel_ax)
        # pos_ax = fig.add_subplot(3, 1, 3, projection="3d")
        pos_ax = fig.add_subplot(1, 1, 1, projection="3d")
        pos_ax.set_title("Position Data from BNO085")
        pos_ax.set_xlabel("X (m)")
        pos_ax.set_ylabel("Y (m)")
        pos_ax.set_zlabel("Z (m)")
        pos_sc = pos_ax.scatter(posr[:,0], posr[:,1], posr[:,2], c=t-t[0])
        fig.colorbar(pos_sc, ax=pos_ax)
        plt.show()

        if output:
            output.close()

        sys.exit()
