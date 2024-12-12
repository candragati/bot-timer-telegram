import subprocess
from datetime import datetime
import time
import threading

GROUP_ID = -1001337729941

def waktu():
    while True:
        sekarang    = datetime.now()
        if sekarang.hour == 17:
            pesan = 'jam 17:00'
            bot.send_message(text = pesan,chat_id = GROUP_ID)

def cetak():
    filename = '~/v3/timerbot31.py'
    i = 0
    while True:
        p = subprocess.Popen('python3 '+filename, shell=True).wait()

        if p != 0:
            return ('restart ke {}'.format(i))
            i += 1
            time.sleep(2)
            continue
        else:
            break


# Create an event to signal the threads to stop
event = threading.Event()

# Start the threads
threading.Thread(target=cetak, daemon=True).start()
# threading.Thread(target=waktu, daemon=True).start()

# Wait for the threads to finish
while not event.is_set():
    time.sleep(1)


