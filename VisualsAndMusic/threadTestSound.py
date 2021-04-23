import threading
import time
import sounddevice as sd
import soundfile as sf

C4 = 'samples/C4vH.wav'
DS4 = 'samples/D#4vH.wav'
FS4 = 'samples/F#4vH.wav'
A4 = 'samples/A4vH.wav'

start = time.perf_counter()

def do_something(seconds):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    print(f'Done Sleeping...{seconds}')

def playNote(note_filename):
    data, fs = sf.read(note_filename, dtype='float32') # Extract data and sampling rate from file
    sd.play(data, fs)
    status = sd.wait()  # Wait until file is done playing

threads = []

# for _ in range(0):
#     t = threading.Thread(target=do_something, args=[1.5])
#     t.start()
#     threads.append(t)

t = threading.Thread(target=playNote, args=[C4])
t.start()
threads.append(t)

time.sleep(1)

t = threading.Thread(target=playNote, args=[DS4])
t.start()
threads.append(t)

allThreads = threading.enumerate()

for thread in allThreads:
    print(thread.getName())

for thread in threads:
    thread.join()

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')
