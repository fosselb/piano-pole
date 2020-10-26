import serial
from time import sleep

port = "COM6"           # Windows
# port = "/dev/cu.usbmodem145201"   # macOS

with open("log.csv", "wb") as file:
    ser = serial.Serial(port, 115200, timeout=10)

    for _ in range(1000):
        line = ser.readline()

    # while True:             # Record until stopped (Ctrl+C)
    for _ in range(5000):    # Record n lines
        print("...")
        line = ser.readline()
        file.write(line)
