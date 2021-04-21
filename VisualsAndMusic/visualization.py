from processing_py import *
import csv
import sounddevice as sd
import soundfile as sf
import threading

A3 = 'A3vH.wav'

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
    t = threading.Thread(target=playNote, args=[note_filename])
    t.start()

def stillPlaying():
    allThreads = threading.enumerate()
    # for thread in allThreads:
        # print(thread.getName(), end = '')
    # print('')
    if len(allThreads) > 2:
        return True
    else:
        print('FALSE')
        return False

# setup
app.background(0) # set background
app.fill(255) # set white circle to represent pole
app.ellipse(width/2, height/2, 40, 40)

createSoundThread(A3) # Creates THREAD 2

# draw
while True:
# for i in range(500):

    app.fill(0, 255, 0)
    app.ellipse(x1[i] + width/2, y1[i] + height/2, circle_diameter, circle_diameter)
    app.fill(255, 0, 0)
    app.ellipse(x2[i] + width/2, y2[i] + height/2, circle_diameter, circle_diameter)
    app.fill(0, 0, 255)
    app.ellipse(x3[i] + width/2, y3[i] + height/2, circle_diameter, circle_diameter)
    app.fill(255, 255, 0)
    app.ellipse(x4[i] + width/2, y4[i] + height/2, circle_diameter, circle_diameter)

    if i < len(t) - 1:
        i = i + 1
    else:
        i = 0

    app.redraw() # refresh the window

    decision = stillPlaying()
    if decision == False:
        createSoundThread(A3)





#app.exit() # close the window
