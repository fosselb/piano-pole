import serial

# port = "COM6"           # Windows
port = "/dev/cu.usbmodem145201"   # macOS

with open("log.csv", "wb") as file:
    ser = serial.Serial(port, 9600, timeout=10)

    # while True:             # Record until stopped (Ctrl+C)
    for _ in range(500):    # Record n lines
        line = ser.readline()
        file.write(line)
