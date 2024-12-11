import subprocess
from datetime import datetime
import time
import threading
import tarfile
import os
import requests

namaLog = "sarbot.log"

def tanggal():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %X')

def tulisLogAkhir(teks):
    file = open(namaLog,'r')
    lines = file.readlines()[:-1]
    lines.append(f"{tanggal()} {teks}\nreading...")
    file.close()
    file = open(namaLog,'w')
    file.writelines(lines)
    file.close()
    
def waktu():
    while True:
        time.sleep(40)
        sekarang    = datetime.now()
        if sekarang.hour == 18 and sekarang.minute == 00:
            now     = datetime.now()
            tanggal = now.strftime("%d%m%Y-%H%M%S")
            namaFile= f"sarbot{tanggal}.tar.gz"
            tar     = tarfile.open(namaFile, "w:gz")

            for root, dirs, files in os.walk(os.getcwd()):
                for name in files:
                    if (name.endswith((".py",".py")) or name == 'database'):
                        tar.add(os.path.join(root, name))
            tar.close()

            bot_token   = "609147123:AAF-dfXuUj8rX8r1peMkQVvZg5BKlJv-Buc" # @srabatsrobot
            bot_chatId  = -1001337729941
            akhir       = datetime.now()
            selisih     = (akhir-now).seconds

            a = open(namaFile, 'rb')
            send_document = 'https://api.telegram.org/bot' + bot_token +'/sendDocument?'
            data = {
              'chat_id'     : bot_chatId,
              'parse_mode'  : 'HTML',
              'caption'     : f"{now}\n{akhir}\n\n{selisih} detik"
               }

            r = requests.post(send_document, data=data, files={'document': a},stream=True)

def cetak():
    filename = '~/v3/timerbot31.py'
    i = 0
    while True:
        p = subprocess.Popen('python3 '+filename, shell=True).wait()
        if p != 0:            
            i += 1
            teks = f"restart ke {i}"
            tulisLogAkhir(teks)
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


