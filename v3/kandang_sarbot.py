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
BOT_CHAT_ID = Config.BOT_CHAT_ID       

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

def send_telegram_message(message):
    """Mengirim pesan ke Telegram melalui bot."""
    send_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': BOT_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(send_url, data=data)
    if response.status_code != 200:
        print(f"Gagal mengirim pesan: {response.status_code}, {response.text}")
        
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
    max_restarts = 5
    cooldown_time = 300
    process = None

    while True:
        try:
            # Jalankan git pull dan script baru jika tidak ada process
            if process is None:
                try:
                    pull_result = subprocess.run(
                        ['git', 'pull', 'origin', 'master'],
                        cwd=script_dir, 
                        capture_output=True, 
                        text=True, 
                        check=True
                    )
                    output = pull_result.stdout.strip()
                    message = f"Bot Berhasil Dimulai Ulang dengan Pull Terbaru!\nOutput:\n<pre>{output}</pre>"
                    send_telegram_message(message)
                    print("Git pull berhasil.")
                    
                except subprocess.CalledProcessError as e:
                    print(f"Gagal melakukan git pull: {e}")
                    message = f"Bot Berhasil Dimulai Ulang namun gagal melakukan git Pull Terbaru!\nError: <pre>{e}</pre>"
                    send_telegram_message(message)

                # Jalankan script
                process = subprocess.Popen(
                    ['python3', script_path],
                    preexec_fn=os.setsid,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"Script started with PID: {process.pid}")

            # Monitor process yang sedang berjalan
            try:
                exit_code = process.poll()  # Cek status tanpa blocking
                
                if exit_code is not None:  # Process berhenti
                    if exit_code != 0:  # Error terjadi
                        restart_count += 1
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        log_text = f"[{timestamp}] Restart ke {restart_count}"
                        write_log_entry(log_text)
                        
                        _, stderr = process.communicate()
                        error_message = f"Script error (code {exit_code}):\n{stderr.decode()}"
                        send_telegram_message(f"Bot Error!\n<pre>{error_message}</pre>")
                        
                        print(f"Script keluar dengan kode {exit_code}. Me-restart...")
                        
                        if restart_count >= max_restarts:
                            cooldown_message = f"Terlalu banyak restart ({restart_count}). Cooling down for {cooldown_time/60} minutes..."
                            print(cooldown_message)
                            send_telegram_message(cooldown_message)
                            time.sleep(cooldown_time)
                            restart_count = 0
                        
                        # Cleanup dan reset process
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except (ProcessLookupError, OSError) as e:
                            print(f"Error killing process: {e}")
                        process = None
                        time.sleep(2)
                        
                    else:  # Script berhenti normal
                        print("Script berhenti normal, me-restart...")
                        process = None
                        restart_count = 0
                        time.sleep(2)
                
                else:  # Process masih berjalan
                    time.sleep(2)  # Tunggu sebentar sebelum cek lagi
                    
            except KeyboardInterrupt:
                print("\nDiterima KeyboardInterrupt. Menghentikan script...")
                if process:
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        process.wait(timeout=5)  # Tunggu process berhenti
                    except (ProcessLookupError, OSError, subprocess.TimeoutExpired) as e:
                        print(f"Error during cleanup: {e}")
                break

        except Exception as e:
            error_message = f"Monitor error: {str(e)}"
            print(error_message)
            send_telegram_message(f"Monitor Error!\n<pre>{error_message}</pre>")
            
            # Cleanup jika terjadi error
            if process:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except (ProcessLookupError, OSError) as e:
                    print(f"Error killing process during error handling: {e}")
                process = None
            time.sleep(5)
            
def main():
    # Mulai fungsi monitor_script dan schedule_backup dalam thread terpisah
    monitor_thread = threading.Thread(target=monitor_script, daemon=True)
    backup_thread = threading.Thread(target=schedule_backup, daemon=True)
    
    try:
        monitor_thread.start()
        backup_thread.start()
        
        # Tunggu threads
        monitor_thread.join()
        backup_thread.join()
        
    except KeyboardInterrupt:
        print("\nReceived KeyboardInterrupt in main thread. Exiting...")
    except Exception as e:
        print(f"Error in main thread: {e}")
    finally:
        print("Cleanup complete. Exiting...")
        
if __name__ == "__main__":
    main()
