import argparse
from contextlib import redirect_stderr, redirect_stdout
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

        byteNum = None
        length = None
        checksum = 0

        while True:
            if not self.XBee.in_waiting:
                continue

            current = self.XBee.read()
            current = int.from_bytes(current, byteorder="big")

            if current == START_BYTE:
                message = ""
                byteNum = 0
            elif byteNum == None:
                continue

            if byteNum > 2:
                checksum += current

            if byteNum == 2:
                length = (previous << 8) | current
                length += 3     # Include start and length bytes but NOT checksum byte
            elif byteNum == 5:
                address = (previous << 8) | current
            elif byteNum >= 8 and byteNum < length:
                message += chr(current)
            elif byteNum == length:
                message = message.replace("\r", "")
                if (checksum & 0xFF) != 0xFF:
                    message = None
                return address, message

            previous = current
            byteNum += 1


def parse_args():
    parser = argparse.ArgumentParser(description="Track the position of a Piano Pole performer.")
    exclusive = parser.add_mutually_exclusive_group()
    exclusive.add_argument("-p", "--port", default="COM8", help="Serial port to listen to")
    exclusive.add_argument("-i", "--input", help="File to read from")
    parser.add_argument("-o", "--output", help="File to write to")
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

def get_next_reading(input, output):
    heights = {244: 1, 38: 1, 227: 1, 204: 1, 178: 2, 181: 2, 190: 2, 16: 2, 108: 100}

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
        height = heights[tag]
        reading["data"] = [t_k, height]
    return reading

def visualize(visualization, color=0, x=None, y=None):
    colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
    width = visualization.width
    height = visualization.height
    xyscale = 10000
    performer_diameter = 40
    pole_diameter = 100

    if x != None and y != None:
        visualization.fill(*colors[color % len(colors)])
        visualization.ellipse(width / 2 + x * xyscale, height / 2 + y * xyscale, performer_diameter, performer_diameter)
    visualization.fill(255)
    visualization.ellipse(width / 2, height / 2, pole_diameter, pole_diameter)
    visualization.redraw()

def musicalize(height):
    notes = ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    playsound("piano_samples/" + notes[height] + ".mp3", block=False)


if __name__ == "__main__":
    args = parse_args()
    input = get_input(args)
    output = get_output(args)

    with redirect_stderr(None), redirect_stdout(None):
        visualization = processing.App(2000, 2000)
    visualization.background(0)
    visualize(visualization)

    kalman = KalmanFilter(dim_x=9, dim_z=3)
    kalman.P = np.diag([0, 0, 20, 0, 0, 20, 0, 0, 20])

    t = {}
    pos = np.zeros((1, 3))
    vel = np.zeros((1, 3))
    acc = np.zeros((1, 3))

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
            # reading = get_next_reading(input, output)
            addr = reading["address"]
            type = reading["type"]

            if type == "i":
                t_k, accr_k, acc_k, quat_k, stability_k = reading["data"]
            elif type == "r":
                t_k, height = reading["data"]

            try:
                t[addr] = np.append(t[addr], t_k)
            except KeyError:
                t[addr] = np.array([t_k])
                continue

            dt = t[addr][-1] - t[addr][-2]

            F_block = np.array([[1, dt, dt**2/2], [0, 1, dt], [0, 0, 1]])
            if type == "i":
                kalman.R = np.diag([0.5, 0.5, 0.5])
                H_block = np.array([0, 0, 1])
                if stability_k != 4:
                    F_block = np.array([[1, 0, 0], [0, 0, 0], [0, 0, 0]])
            elif type == "r":
                kalman.R = np.diag([0.001, 0.001, 0.001])
                H_block = np.array([1, 0, 0])

            kalman.H = block_diag(H_block, H_block, H_block)
            kalman.F = block_diag(F_block, F_block, F_block)
            Q_block = Q_discrete_white_noise(dim=3, dt=dt, var=1)
            kalman.Q = block_diag(Q_block, Q_block, Q_block)

            kalman.predict()
            if type == "i":
                kalman.update(accr_k)
            elif type == "r":
                kalman.update(np.array([0, 0, height]))

            pos_k, vel_k, acc_k = kalman.x.reshape((3, 3), order="F")
            pos = np.vstack((pos, pos_k))
            vel = np.vstack((vel, vel_k))
            acc = np.vstack((acc, acc_k))

            visualize(visualization, addr, pos_k[0], pos_k[1])
            for threshold in range(15):
                # if np.sqrt(pos[-1][0]**2 + pos[-1][1]**2) < 0.5:
                if pos[-2][2] < threshold / 3 and pos[-1][2] >= threshold / 3:
                    musicalize(threshold)
                    break
                elif pos[-2][2] > threshold / 3 and pos[-1][2] <= threshold / 3:
                    musicalize(threshold - 1)
                    break

    except (KeyboardInterrupt, StopIteration):
        fig = plt.figure()
        # acc_ax = fig.add_subplot(3, 1, 1, projection="3d")
        # acc_ax.set_title("Acceleration Data from BNO085")
        # acc_ax.set_xlabel("X (m/s^2)")
        # acc_ax.set_ylabel("Y (m/s^2)")
        # acc_ax.set_zlabel("Z (m/s^2)")
        # acc_sc = acc_ax.scatter(accr[:,0], accr[:,1], accr[:,2], c=t-t[0])
        # fig.colorbar(acc_sc, ax=acc_ax)
        # vel_ax = fig.add_subplot(3, 1, 2, projection="3d")
        # vel_ax.set_title("Velocity Data from BNO085")
        # vel_ax.set_xlabel("X (m/s)")
        # vel_ax.set_ylabel("Y (m/s)")
        # vel_ax.set_zlabel("Z (m/s)")
        # vel_sc = vel_ax.scatter(velr[:,0], velr[:,1], velr[:,2], c=t-t[0])
        # fig.colorbar(vel_sc, ax=vel_ax)
        # pos_ax = fig.add_subplot(3, 1, 3, projection="3d")
        # pos_ax = fig.add_subplot(1, 1, 1, projection="3d")
        # pos_ax.set_title("Position Data from BNO085")
        # pos_ax.set_xlabel("X (m)")
        # pos_ax.set_ylabel("Y (m)")
        # pos_ax.set_zlabel("Z (m)")
        # pos_sc = pos_ax.scatter(pos[:,0], pos[:,1], pos[:,2])
        # fig.colorbar(pos_sc, ax=pos_ax)
        # plt.show()

    finally:
        if output:
            output.close()

        try:
            while True:
                pass
        except:
            visualization.exit()
