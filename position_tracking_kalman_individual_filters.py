import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
from serial import Serial, SerialException
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.spatial.transform import Rotation
from scipy.linalg import block_diag


TAG_HEIGHTS = {244: 1, 38: 1, 227: 1, 204: 1, 178: 2, 181: 2, 190: 2, 16: 2, 108: 100}


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
        height = TAG_HEIGHTS[tag]
        reading["data"] = [t_k, height]
    return reading


if __name__ == "__main__":
    args = parse_args()
    input = get_input(args)
    output = get_output(args)

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
                except KeyboardInterrupt:
                    raise(KeyboardInterrupt)
                except:
                    pass
            # reading = get_next_reading(input, output)
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
                kalman[addr].R = np.diag([0.01, 0.01, 0.01])
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

            x_k = kalman[addr].x.reshape((3, 3), order="F")
            pos[addr] = np.vstack((pos[addr], x_k[0]))
            vel[addr] = np.vstack((vel[addr], x_k[1]))
            acc[addr] = np.vstack((acc[addr], x_k[2]))

    except (StopIteration, KeyboardInterrupt):
        for addr in kalman.keys():
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
            pos_ax = fig.add_subplot(1, 1, 1, projection="3d")
            pos_ax.set_title("Position Data from System " + str(addr))
            pos_ax.set_xlabel("X (m)")
            pos_ax.set_ylabel("Y (m)")
            pos_ax.set_zlabel("Z (m)")
            pos_sc = pos_ax.scatter(pos[addr][:,0], pos[addr][:,1], pos[addr][:,2], c=t[addr]-t[addr][0])
            fig.colorbar(pos_sc, ax=pos_ax)
            plt.show()

        if output:
            output.close()

        sys.exit()
