import serial

port = "COM6"   # Windows
# port = "/dev/cu.usbmodem145401"     # macOS

with open("logBNO085-stability.csv", "wb") as file:
    ser = serial.Serial(port, 115200, timeout=10)

    for _ in range(100):
        line = ser.readline()

    i = 0
    while True:         # Record until stopped (Ctrl+C)
    # while i < 10000:    # Record n lines
        if (i % 500 == 0):
            print(".")
        line = ser.readline()
        file.write(line)
        i += 1
