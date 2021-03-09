import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import serial
from filterpy.kalman import KalmanFilter
from serial import SerialException
from scipy.spatial.transform import Rotation


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

def get_source():
    if args.input == None:
        try:
            source = serial.Serial(args.port, 115200, timeout=10)
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

def get_next_reading():
    line = source.readline()
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    if args.output != None:
        output.write(line)
    line = line.strip()
    if line.endswith(","):
        line = line[:-1]
    data = np.array(list(map(float, line.split(","))))

    t_k = data[0]
    acc_k = data[1:5]
    quat_k = data[5:11]
    stability_k = data[11]
    return t_k, acc_k, quat_k, stability_k


if __name__ == "__main__":
    args = parse_args()
    source = get_source()
    if args.output != None:
        output = open(args.output, "w")

    t = np.empty((0, 1))
    accr = np.empty((0, 3))
    velr = np.empty((0, 3))
    posr = np.empty((0, 3))

    try:
        while True:
            reading = get_next_reading()
            t = np.vstack((t, reading[0]))
            acc_k, quat_k, stability_k = reading[1:4]

            accr_k = Rotation.from_quat(quat_k[0:4]).apply(acc_k[0:3])
            accr = np.vstack((accr, accr_k))
            velr_k = velr[-1] + (accr[-1] + accr[-2]) / 2 * (t[-1] - t[-2]) if accr.shape[0] > 1 else np.zeros((1, 3))
            velr = np.vstack((velr, velr_k))
            posr_k = posr[-1] + (velr[-1] + velr[-2]) / 2 * (t[-1] - t[-2]) if velr.shape[0] > 1 else np.zeros((1, 3))
            posr = np.vstack((posr, posr_k))

    except (StopIteration, KeyboardInterrupt):
        fig = plt.figure()
        acc_ax = fig.add_subplot(3, 1, 1, projection="3d")
        acc_ax.set_title("Acceleration Data from BNO085")
        acc_ax.set_xlabel("X (m/s^2)")
        acc_ax.set_ylabel("Y (m/s^2)")
        acc_ax.set_zlabel("Z (m/s^2)")
        acc_sc = acc_ax.scatter(accr[:,0], accr[:,1], accr[:,2], c=t-t.flat[0])
        fig.colorbar(acc_sc, ax=acc_ax)
        vel_ax = fig.add_subplot(3, 1, 2, projection="3d")
        vel_ax.set_title("Velocity Data from BNO085")
        vel_ax.set_xlabel("X (m/s)")
        vel_ax.set_ylabel("Y (m/s)")
        vel_ax.set_zlabel("Z (m/s)")
        vel_sc = vel_ax.scatter(velr[:,0], velr[:,1], velr[:,2], c=t-t.flat[0])
        fig.colorbar(vel_sc, ax=vel_ax)
        pos_ax = fig.add_subplot(3, 1, 3, projection="3d")
        pos_ax.set_title("Position Data from BNO085")
        pos_ax.set_xlabel("X (m)")
        pos_ax.set_ylabel("Y (m)")
        pos_ax.set_zlabel("Z (m)")
        pos_sc = pos_ax.scatter(posr[:,0], posr[:,1], posr[:,2], c=t-t.flat[0])
        fig.colorbar(pos_sc, ax=pos_ax)
        plt.show()

        sys.exit()
