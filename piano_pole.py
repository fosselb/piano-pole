# piano_pole.py
# Author: Fosse Lin-Bianco and Evan Mitchell
# Purpose: Visualize and musicalize a Piano Pole performance.
# Usage: `piano_pole.py [-h] [-p PORT | -i INPUT] [-o OUTPUT] [-t] [-r]`
# For sample output: `python piano_pole.py -t -i logs/log7.txt`

import argparse
from contextlib import redirect_stderr, redirect_stdout
from time import time, sleep
import sys

import matplotlib.pyplot as plt
import numpy as np
from playsound import playsound
import processing_py as processing
from filterpy.common import Q_discrete_white_noise
from filterpy.kalman import KalmanFilter
from scipy.linalg import block_diag
from scipy.spatial.transform import Rotation
from serial import Serial, SerialException


HEIGHTS = {244: 1, 38: 1, 227: 1, 204: 1, 178: 2, 181: 2, 190: 2, 16: 2, 108: 100}  # last byte of tag id: height (m)
COLORS = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
NOTES = ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]


class File_Reader:
    def __init__(self, filename):
        with open(filename, "r") as file:
            contents = file.read()
            self.messages = iter(contents.split("<")[1:])

    def read(self):
        address, message = next(self.messages).split(">\n")
        address = int(address)
        message = message.removesuffix("\n\n")
        if message == "E":
            message = None
        return address, message


class XBee_Reader:
    def __init__(self, port):
        self.XBee = Serial(port, 115200)

    def read(self):
        START_BYTE = 0x7E

        byte_num = None
        length = None
        checksum = 0

        while True:
            if not self.XBee.in_waiting:
                continue

            current = self.XBee.read()
            current = int.from_bytes(current, byteorder="big")

            if current == START_BYTE:
                message = ""
                byte_num = 0
            elif byte_num == None:
                continue

            if byte_num > 2:
                checksum += current

            if byte_num == 2:
                length = (previous << 8) | current
                length += 3  # Include start and length bytes but NOT checksum byte
            elif byte_num == 5:
                address = (previous << 8) | current
            elif byte_num >= 8 and byte_num < length:
                message += chr(current)
            elif byte_num == length:
                message = message.replace("\r", "")
                if (checksum & 0xFF) != 0xFF:
                    message = None
                return address, message

            previous = current
            byte_num += 1


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize and musicalize a Piano Pole performance.")
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument("-p", "--port", default="COM8", help="serial port to listen to (default COM8)")
    exclusive.add_argument("-i", "--input", help="file to read from")
    parser.add_argument("-o", "--output", help="file to write to")
    parser.add_argument("-t", "--time", help="play back in real time", action="store_true")
    parser.add_argument("-r", "--recording", help="play beep at start for recording purposes", action="store_true")
    return parser.parse_args()

def get_input(args):
    if args.input == None:
        try:
            return XBee_Reader(args.port)
        except SerialException:
            sys.exit("Port '" + args.port + "' not available")
    else:
        try:
            return File_Reader(args.input)
        except FileNotFoundError:
            sys.exit("Input file '" + args.input + "' not found")

def get_output(args):
    if args.output == None:
        return None
    try:
        return open(args.output, "w")
    except:
        sys.exit("Unable to create output file '" + args.output + "'")

def get_next_message(input, output):
    address, message = input.read()
    if output:
        message_str = message if message != None else "E"
        output.write("<" + str(address) + ">\n" + message_str + "\n\n")
    return address, message

existing = dict()
def get_next_line(input, output):
    line = None
    for address, lines in existing.items():
        if len(lines) > 1:
            line = lines.pop(0)
            break
    while line == None:
        message = None
        while message == None:
            address, message = get_next_message(input, output)
            if message == None:
                existing[address] = []
        lines = message.split("\n")

        try:
            beginning = existing[address].pop(0)
        except (KeyError, IndexError):
            if not (lines[0].startswith("i") or lines[0].startswith("r")):
                lines.pop(0)
        else:
            lines[0] = beginning + lines[0]

        if len(lines) > 0:
            if len(lines) > 1:
                line = lines.pop(0)
            existing[address] = lines
    return address, line

play_times = {}
def get_next_reading(input, output):
    address, line = get_next_line(input, output)
    # print(str(address) + ": " + line)
    data = line.strip(",").split(",")
    reading = {"address": address, "type": data.pop(0)}
    data = np.array([float(datum) for datum in data])
    if reading["type"] == "i":
        t_k = data[0]
        acc_k = data[1:5]
        quat_k = data[5:11]
        stability_k = data[11]
        accr_k = Rotation.from_quat(quat_k[0:4]).apply(acc_k[0:3])
        reading["data"] = [t_k, accr_k, acc_k, quat_k, stability_k]
    elif reading["type"] == "r":
        t_k = data[0]
        tag = data[1]
        height = HEIGHTS[tag]
        reading["data"] = [t_k, height]

    if args.time:
        try:
            diff = play_times[address]
        except KeyError:
            play_times[address] = time() - t_k
        else:
            sleep_time = t_k + diff - time()
            if sleep_time > 0:
                sleep(sleep_time)

    return reading

def visualize(visualization, color=0, x=None, y=None):
    width = visualization.width
    height = visualization.height
    xyscale = 200
    performer_diameter = 40
    pole_diameter = 100

    if x != None and y != None:
        visualization.fill(*COLORS[color % len(COLORS)])
        visualization.ellipse(width / 2 + x * xyscale, height / 2 + y * xyscale, performer_diameter, performer_diameter)
    visualization.fill(255)
    visualization.ellipse(width / 2, height / 2, pole_diameter, pole_diameter)
    visualization.redraw()

def musicalize(height):
    playsound("piano_samples/" + NOTES[height] + ".mp3", block=False)


if __name__ == "__main__":
    args = parse_args()
    input = get_input(args)
    output = get_output(args)

    with redirect_stderr(None), redirect_stdout(None):
        visualization = processing.App(2000, 2000)
    visualization.background(0)
    visualize(visualization)

    if args.recording:
        sleep(5)
        playsound("piano_samples/beep.mp3", block=False)

    kalman = {}
    t = {}
    pos = {}
    vel = {}
    acc = {}

    try:
        while True:
            reading = None
            while reading == None:
                try:
                    reading = get_next_reading(input, output)
                except (KeyboardInterrupt, StopIteration):
                    raise
                except:
                    pass
            addr = reading["address"]
            type = reading["type"]

            if type == "i":
                t_k, accr_k, acc_k, quat_k, stability_k = reading["data"]
            elif type == "r":
                t_k, height = reading["data"]

            if addr not in kalman.keys():
                kalman[addr] = KalmanFilter(dim_x=9, dim_z=3)
                kalman[addr].P = np.diag([0, 0, 20, 0, 0, 20, 0, 0, 20])

                t[addr] = np.array([t_k])
                pos[addr] = np.zeros((1, 3))
                vel[addr] = np.zeros((1, 3))
                acc[addr] = np.zeros((1, 3))
                continue

            t[addr] = np.append(t[addr], t_k)
            dt = t[addr][-1] - t[addr][-2]

            F_block = np.array([[1, dt, dt**2/2], [0, 1, dt], [0, 0, 1]])
            if type == "i":
                kalman[addr].R = np.diag([0.5, 0.5, 0.5])
                H_block = np.array([0, 0, 1])
                if stability_k != 4:
                    F_block = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
            elif type == "r":
                kalman[addr].R = np.diag([0.001, 0.001, 0.001])
                H_block = np.array([1, 0, 0])

            kalman[addr].H = block_diag(H_block, H_block, H_block)
            kalman[addr].F = block_diag(F_block, F_block, F_block)
            Q_block = Q_discrete_white_noise(dim=3, dt=dt, var=1)
            kalman[addr].Q = block_diag(Q_block, Q_block, Q_block)

            kalman[addr].predict()
            if type == "i":
                kalman[addr].update(accr_k)
            elif type == "r":
                kalman[addr].update(np.array([0, 0, height]))

            pos_k, vel_k, acc_k = kalman[addr].x.reshape((3, 3), order="F")
            pos[addr] = np.vstack((pos[addr], pos_k))
            vel[addr] = np.vstack((vel[addr], vel_k))
            acc[addr] = np.vstack((acc[addr], acc_k))

            visualize(visualization, addr, pos_k[0], pos_k[1])
            for threshold in range(15):
                # if np.sqrt(pos[addr][-1][0]**2 + pos[addr][-1][1]**2) < 0.5:
                if pos[addr][-2][2] < threshold / 3 and pos[addr][-1][2] >= threshold / 3 and threshold < 14:
                    musicalize(threshold + 1)
                    break
                elif pos[addr][-2][2] > threshold / 3 and pos[addr][-1][2] <= threshold / 3:
                    musicalize(threshold)
                    break

    except (KeyboardInterrupt, StopIteration):
        for addr in kalman.keys():
            fig = plt.figure()
            # acc_ax = fig.add_subplot(3, 1, 1, projection="3d")
            # acc_ax.set_title("Acceleration Data from System " + str(addr))
            # acc_ax.set_xlabel("X (m/s^2)")
            # acc_ax.set_ylabel("Y (m/s^2)")
            # acc_ax.set_zlabel("Z (m/s^2)")
            # acc_sc = acc_ax.scatter(acc[addr][:,0], acc[addr][:,1], acc[addr][:,2], c=t[addr]-t[addr][0])
            # fig.colorbar(acc_sc, ax=acc_ax)
            # vel_ax = fig.add_subplot(3, 1, 2, projection="3d")
            # vel_ax.set_title("Velocity Data from System " + str(addr))
            # vel_ax.set_xlabel("X (m/s)")
            # vel_ax.set_ylabel("Y (m/s)")
            # vel_ax.set_zlabel("Z (m/s)")
            # vel_sc = vel_ax.scatter(vel[addr][:,0], vel[addr][:,1], vel[addr][:,2], c=t[addr]-t[addr][0])
            # fig.colorbar(vel_sc, ax=vel_ax)
            pos_ax = fig.add_subplot(1, 1, 1, projection="3d")          # pos_ax = fig.add_subplot(3, 1, 3, projection="3d")
            pos_ax.set_title("Position Data from System " + str(addr))
            pos_ax.set_xlabel("X (m)")
            pos_ax.set_ylabel("Y (m)")
            pos_ax.set_zlabel("Z (m)")
            pos_sc = pos_ax.scatter(pos[addr][:, 0], pos[addr][:, 1], pos[addr][:, 2], c=t[addr] - t[addr][0])
            fig.colorbar(pos_sc, ax=pos_ax)
            plt.show()

    finally:
        if output:
            output.close()

        try:
            while True:
                pass
        except:
            visualization.exit()
