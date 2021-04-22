import threading
import time

start = time.perf_counter()

def do_something(seconds):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    print(f'Done Sleeping...{seconds}')

threads = []

for _ in range(0):
    t = threading.Thread(target=do_something, args=[1.5])
    t.start()
    threads.append(t)

allThreads = threading.enumerate()
print(f'first length: {len(allThreads)}')
for thread in allThreads:
    print(thread.getName())

for thread in threads:
    thread.join()

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')
