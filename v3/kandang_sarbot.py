from config import Config
import subprocess
import time
import threading
import tarfile
import os
import requests
import datetime
import signal

BOT_TOKEN = Config.TOKEN 
BOT_CHAT_ID = -1001337729941       

LOG_FILE = "sarbot.log"  # Nama file log

def get_current_time_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %X')

def write_log_entry(text):
    try:
        with open(LOG_FILE, 'r') as file:
            lines = file.readlines()
            # Hapus baris terakhir jika file tidak kosong
            if lines:
                lines = lines[:-1]
    except FileNotFoundError:
        # Jika file log tidak ada, mulai dengan daftar kosong
        lines = []

    # Tambahkan entri log baru
    lines.append(f"{get_current_time_str()} {text}\nreading...\n")

    with open(LOG_FILE, 'w') as file:
        file.writelines(lines)

def backup_and_send():
    now = datetime.datetime.now()
    timestamp = now.strftime("%d%m%Y-%H%M%S")
    backup_filename = f"sarbot{timestamp}.tar.gz"

    # Membuat file tar.gz dengan file .py dan folder 'database'
    with tarfile.open(backup_filename, "w:gz") as tar:
        for root, dirs, files in os.walk(os.getcwd()):
            for name in files:
                if name.endswith(".py") or name == 'database':
                    tar.add(os.path.join(root, name))

    # Menghitung durasi proses backup
    end_time = datetime.datetime.now()
    duration_seconds = int((end_time - now).total_seconds())

    # Mempersiapkan pengiriman file melalui Telegram
    with open(backup_filename, 'rb') as file_data:
        send_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendDocument'
        data = {
            'chat_id': BOT_CHAT_ID,
            'parse_mode': 'HTML',
            'caption': f"{now}\n{end_time}\n\n{duration_seconds} detik"
        }
        files = {'document': file_data}

        response = requests.post(send_url, data=data, files=files)
        if response.status_code != 200:
            print(f"Gagal mengirim dokumen: {response.status_code}, {response.text}")

def schedule_backup():
    while True:
        now = datetime.datetime.now()
        # Atur waktu target ke pukul 18:00 hari ini
        target_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        # Jika sudah melewati pukul 18:00, jadwalkan untuk hari berikutnya
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
        sleep_seconds = (target_time - now).total_seconds()
        print(f"Backup dijadwalkan dalam {sleep_seconds} detik.")
        time.sleep(sleep_seconds)
        backup_and_send()

def monitor_script():
    script_path = os.path.expanduser('~/v3/v3/timerbot31.py')
    script_dir = os.path.dirname(script_path)
    restart_count = 0
    while True:
        # Sebelum menjalankan script, lakukan git pull origin master
        try:
            subprocess.run(['git', 'pull', 'origin', 'master'], cwd=script_dir, check=True)
            print("Git pull berhasil.")
        except subprocess.CalledProcessError as e:
            print(f"Gagal melakukan git pull: {e}")
        process = subprocess.Popen(['python3', script_path], preexec_fn=os.setsid)
        try:
            exit_code = process.wait()
        except KeyboardInterrupt:
            print("Diterima KeyboardInterrupt. Menghentikan script...")
            # Menghentikan semua proses dalam grup proses
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            break
        if exit_code != 0:
            # Jika script keluar dengan error, restart
            restart_count += 1
            log_text = f"restart ke {restart_count}"
            write_log_entry(log_text)
            print(f"Script keluar dengan kode {exit_code}. Me-restart...")
            # Menghentikan semua proses anak yang tersisa
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            time.sleep(2)
        else:
            # Keluar dari loop jika script selesai dengan sukses
            print("Script selesai dengan sukses.")
            break

def main():
    # Mulai fungsi monitor_script dan schedule_backup dalam thread terpisah
    threading.Thread(target=monitor_script, daemon=True).start()
    threading.Thread(target=schedule_backup, daemon=True).start()

    # Menjaga thread utama tetap berjalan
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
