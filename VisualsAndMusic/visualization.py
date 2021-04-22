from processing_py import *
import csv
import sounddevice as sd
import soundfile as sf
import threading

C4 = 'samples/C4vH.wav'
DS4 = 'samples/D#4vH.wav'
FS4 = 'samples/F#4vH.wav'
A4 = 'samples/A4vH.wav'

height = 800
width = 800
circle_diameter = 10;
t = []
x1 = []
y1 = []
x2 = []
y2 = []
x3 = []
y3 = []
x4 = []
y4 = []
i = 0

app = App(width,height) # create window: width, height. Creates THREAD 1

with open("rose_data.csv") as csv_file:
    csv_reader = csv.reader(csv_file)
    for lines in csv_reader:
      t.append(lines[0])
      x1.append(lines[1])
      y1.append(lines[2])
      x2.append(lines[3])
      y2.append(lines[4])
      x3.append(lines[5])
      y3.append(lines[6])
      x4.append(lines[7])
      y4.append(lines[8])

t = [int(i) for i in t]
x1 = [int(i) for i in x1]
y1 = [int(i) for i in y1]
x2 = [int(i) for i in x2]
y2 = [int(i) for i in y2]
x3 = [int(i) for i in x3]
y3 = [int(i) for i in y3]
x4 = [int(i) for i in x4]
y4 = [int(i) for i in y4]

def playNote(note_filename):
    data, fs = sf.read(note_filename, dtype='float32') # Extract data and sampling rate from file
    sd.play(data, fs)
    status = sd.wait()  # Wait until file is done playing

def createSoundThread(note_filename):
    threadName = note_filename
    t = threading.Thread(name=threadName, target=playNote, args=[note_filename])
    t.start()
    print('thread started')

def stillPlaying(note_filename):
    allThreads = threading.enumerate()
    for thread in allThreads:
        print(thread.getName(), end = '')
    print('')
    for thread in allThreads:
        if thread.getName() == note_filename:
            return True

    return False
    # if len(allThreads) > 2:
    #     return True
    # else:
    #     print('FALSE')
    #     return False

# setup
app.background(0) # set background
app.fill(255) # set white circle to represent pole
app.ellipse(width/2, height/2, 40, 40)

# createSoundThread(A3) # Creates THREAD 2
tolerance = 2;

# draw
while True:
    x1_coor = x1[i] + width/2
    y1_coor = y1[i] + height/2
    x2_coor = x2[i] + width/2
    y2_coor = y2[i] + height/2

    app.fill(0, 255, 0)
    app.ellipse(x1_coor, y1_coor, circle_diameter, circle_diameter)
    app.fill(255, 0, 0)
    app.ellipse(x2_coor, y2_coor, circle_diameter, circle_diameter)
    app.fill(0, 0, 255)
    app.ellipse(x3[i] + width/2, y3[i] + height/2, circle_diameter, circle_diameter)
    app.fill(255, 255, 0)
    app.ellipse(x4[i] + width/2, y4[i] + height/2, circle_diameter, circle_diameter)

    if (x1_coor > 400 - tolerance and x1_coor < 400 + tolerance):
        if (y1_coor > 400 - tolerance and y1_coor < 400 + tolerance):
            if stillPlaying(C4) == False:
                createSoundThread(C4)

    if (x2_coor > 400 - tolerance and x2_coor < 400 + tolerance):
        if (y2_coor > 400 - tolerance and y2_coor < 400 + tolerance):
            if stillPlaying(DS4) == False:
                createSoundThread(DS4)

    if i < len(t) - 1:
        i = i + 1
    else:
        i = 0

    app.redraw() # refresh the window







#app.exit() # close the window
