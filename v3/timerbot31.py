from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import MessageEntity
from telegram import ParseMode, Update, Bot, Message 
from telegram.utils.helpers import escape_markdown
from telegram import InputMediaPhoto, InputMediaVideo
from concurrent.futures import ThreadPoolExecutor
import requests
import signal
import subprocess
import logging
import datetime
import re
import time
import threading
import requests
from config import *
from modul import me,bio,afk,qotd,langdetect,setting,berita,rekam,asl,bantuan,media, reputasi, kawalCorona
from modul.kamus import kamus
from tempfile import TemporaryDirectory
import pprint
import sqlite3
import tarfile
import os
from urllib.parse import urlparse, quote


pathDB = "database"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

class bot_timer():
    def __init__(self):
        self.koneksiDatabase()
        self.t1 = threading.Thread(target=self.timer)
        self.t1.start()
        updater = Config.updater
        dp = Config.dp

        dp.add_handler(CommandHandler("restart_pull",              self.restart_pull))
        dp.add_handler(CommandHandler("start",              self.start))
        dp.add_handler(CommandHandler("afk",                afk.set_afk))
        dp.add_handler(CommandHandler("setbio",             bio.set_bio))
        dp.add_handler(CommandHandler("bio",                bio.bio))
        dp.add_handler(CommandHandler("setme",              me.set_me))
        dp.add_handler(CommandHandler("me",                 me.me))
        dp.add_handler(CommandHandler("qotd",               qotd.qotd,      pass_args = True))
        dp.add_handler(CommandHandler("dqotd",              qotd.dqotd,     pass_args = True))
        dp.add_handler(CommandHandler("xqotd",              qotd.xqotd,     pass_args = True))
        dp.add_handler(CommandHandler("rqotd",              qotd.rqotd))
        dp.add_handler(CommandHandler("sqotd",              qotd.sqotd,     pass_args = True))
        dp.add_handler(CommandHandler("setting",            setting.setting,pass_args = True))
        dp.add_handler(CommandHandler("berita",             berita.berita,  pass_args = True))
        dp.add_handler(CommandHandler("baca",               rekam.baca))
        dp.add_handler(CommandHandler("tulis",              rekam.tulis))
        dp.add_handler(CommandHandler("judul",              rekam.judul))
        dp.add_handler(CommandHandler("help",               bantuan.help))
        dp.add_handler(CommandHandler("help_qotd",          bantuan.help_qotd))
        dp.add_handler(CommandHandler("help_timer",         bantuan.help_timer))
        dp.add_handler(CommandHandler("help_jadwal_sholat", bantuan.help_jadwal_sholat))
        dp.add_handler(CommandHandler("agenda",             self.agenda))
        dp.add_handler(CommandHandler("media",              media.media,    pass_args = True))
        dp.add_handler(CommandHandler("smedia",             media.smedia,   pass_args = True))
        dp.add_handler(CommandHandler("xmedia",             media.xmedia))
        dp.add_handler(CommandHandler("rmedia",             media.rmedia))
        dp.add_handler(CommandHandler("cm",                 media.cmedia))
        # dp.add_handler(CommandHandler("umedia",             umedia.echo))
        # dp.add_handler(CommandHandler("usmedia",             umedia.smedia))
        dp.add_handler(CommandHandler("set",                self.set_timer,
                                      pass_args         =   True,
                                      pass_job_queue    =   True,
                                      pass_chat_data    =   True))
        dp.add_handler(CommandHandler("hitung",             self.timer,
                                      pass_chat_data    =   True, 
                                      pass_job_queue    =   True, 
                                      pass_args         =   True))
        dp.add_handler(CommandHandler("rg",                 reputasi.reputasi_good))
        dp.add_handler(CommandHandler("rb",                 reputasi.reputasi_bad))
        # dp.add_handler(CommandHandler("itungin",            kalkulus.itungin))
        dp.add_handler(CommandHandler("cor",        kawalCorona.cor))
        dp.add_handler(CommandHandler("corstat",        kawalCorona.corGraph, pass_args = True))
        dp.add_handler(CommandHandler("lupaUmur",        asl.lupaUmur))
        dp.add_handler(CommandHandler("setUmur",        asl.setUmur, pass_args = True))
        
        
        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, asl.asl))
        dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION) | Filters.reply ,afk.reply_afk),group = 1)
        dp.add_handler(MessageHandler(Filters.all, langdetect.echo),group = 2)
        dp.add_handler(MessageHandler(Filters.text|Filters.video | Filters.photo | Filters.document | Filters.forwarded | Filters.sticker, rekam.isi), group = 3)
        dp.add_handler(MessageHandler(~Filters.command, afk.sudah_nongol), group = 4)
        dp.add_handler(MessageHandler(Filters.text, asl.check_age),group = 5)
        dp.add_handler(MessageHandler(Filters.text, self.cmedia),group = 6)
        self.check_restart_message()
        updater.start_polling()
        updater.idle()

    def check_restart_message(self):
        try:
            restart_file = "/tmp/bot_restart_info.json"
            if os.path.exists(restart_file):
                with open(restart_file, 'r') as f:
                    data = json.load(f)
                chat_id = data.get('chat_id')
                if chat_id:
                    bot = Bot(token = Config.TOKEN)
                    bot.send_message(
                        chat_id=chat_id,
                        text="✅ Bot berhasil direstart!",
                        parse_mode='Markdown'
                    )
                os.remove(restart_file)
        except Exception as e:
            print(f"Error sending restart message: {e}")
            
    def cmedia(self,update, context):
        bot     = context.bot    
        message = update.message.text
        args    = re.search(r'(https?://[^\s]+)', message)
        if args == None:
            pass
        else:
            args    = args.group()
            chat_id = update.message["chat"]["id"]   
            hostname= urlparse(args).hostname
            arsip   = "http://5.75.163.32:6969/"
            if hostname == 'twitter.com' or hostname == 'x.com':
                sosmed = "api/twit"
            elif ('facebook' in hostname) or ('fb' in hostname):
                sosmed = "api/fb"
            elif 'instagram' in hostname:
                sosmed = "api/ig"
            elif hostname == 'tiktok.com':
                sosmed = "api/tiktok"
            else:                
                return
            
            endpoint= f"?url={quote(args)}"
            link = f"{arsip}{sosmed}{endpoint}"
            req = requests.get(link).json()


            if req['success']:
                medias = []
                media_results = req['media']
                total_media_res = len(media_results)
                if media_results:
                    for i, m in enumerate(media_results):
                        caption = req['caption'] if i == total_media_res - 1 else None
                        read_more = 'Read More...'
                        caption = caption[:1024 - len(read_more)] + f"[{read_more}]({args})" if caption and len(caption) >=1024 else caption
                        if m['type'].upper() != 'VIDEO':
                            if sosmed == "api/fb":
                                medias.append(InputMediaPhoto(m['imageHigh'], caption = caption))
                            else:
                                medias.append(InputMediaPhoto(m['url'], caption = caption))

                        else:
                            if sosmed == "api/fb":
                                medias.append(InputMediaVideo(m['sd_url'], caption = caption))
                            else:
                                medias.append(InputMediaVideo(m['url'], caption = caption))
                if len(medias) == 0:
                    caption = req['caption']
                    update.message.reply_text(caption)
                else:
                    self.reply_downloaded_media_chunk(bot, chat_id, medias)
                    # bot.send_media_group(chat_id = chat_id, media = medias)
            else:
                update.message.reply_text(req.get('msg') or "gagal")
                
    def downloader_media(self, temp_dir, media_url):
        try:
            response = requests.get(media_url, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            extension = '.' + (content_type.split('/')[-1] if '/' in content_type else 'tmp')
            
            filename = f"media_{os.urandom(4).hex()}{extension}"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return {
                'file': filepath,
                'success': True,
                'size': os.path.getsize(filepath)
            }
        
        except Exception as e:
            return {
                'file': None,
                'success': False,
                'error': str(e)
            }
    
    def reply_downloaded_media_chunk(self, bot, chat_id, medias):
        with TemporaryDirectory() as tdir:
            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(
                    lambda m: self.downloader_media(tdir, m.media), 
                    medias
                ))
                
                successful_medias = []
                for media, result in zip(medias, results):
                    if result['success']:
                        with open(result['file'], 'rb') as f:
                            caption = getattr(media, 'caption', None)
                            if media.type == 'photo':
                                media_obj = InputMediaPhoto(f, caption=caption, parse_mode='Markdown')
                            elif media.type == 'video':
                                media_obj = InputMediaVideo(f, caption=caption, parse_mode='Markdown')
                            successful_medias.append(media_obj)
            
            CHUNK_SIZE = 10
            for i in range(0, len(successful_medias), CHUNK_SIZE):
                chunk = successful_medias[i:i + CHUNK_SIZE]
                bot.send_media_group(chat_id=chat_id, media=chunk)
            
    def start(self,update,context):
        try:
            z = self.t1.is_alive()
        except:            
            self.t1 = threading.Thread(target=self.timer)
            self.t1.start()        
        update.message.reply_text(kamus("cmd_start"))

    def set_tanggal(self,update,context,args):
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(update,context,args,int((datetime.datetime.strptime("%s %s"%(args[0], args[1]),"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            update.message.reply_text(kamus("cmd_error"))

    def set_jam(self,update,context, args):
        now = '{:%Y-%m-%d}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(update,context,int((datetime.datetime.strptime(now+" "+args[0],"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            self.set_tanggal(update,context, args)

    def jadwal_sholat(self,update,context, kota):
        try:
            z           = self.t1.is_alive()
            nama        = kota            
            sekarang    = datetime.datetime.now()
            tanggal     = sekarang.strftime('%Y-%m-%d')
            jam         = sekarang.strftime('%H:%M')
            hari        = datetime.datetime.strftime(sekarang.date(),"%a")
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user.username
            cek         = "SELECT waktu FROM daftar_timer WHERE kota = '%s' AND DATE(waktu) = '%s' AND chat_id = '%s'"%(nama,tanggal,chat_id)
            bar, jum    = eksekusi(cek)
            if jum == 0:                
                url_kota= "https://api.banghasan.com/sholat/format/json/kota"
                r       = requests.get(url_kota)
                kota_all= r.json()['kota']
                mirip   = []
                for a in kota_all:
                    if a['nama'] == nama.upper() or a['id'] == nama:
                        if a['id'] == nama: nama = a['nama']
                        update.message.reply_text(str(kamus("id_ketemu"))%a['id'])
                        url         = "https://api.banghasan.com/sholat/format/json/jadwal/kota/%s/tanggal/%s"%(a['id'],tanggal)            
                        r           = requests.get(url)
                        sholat_all  =  r.json()['jadwal']['data']
                        jadwal      = []
                        t           = ""
                        m           = ""
                        for k,v in sholat_all.items():
                            if k != 'tanggal':
                                waktu = '%s %s:00'%(tanggal,v)
                                if k == 'terbit' or k == 'imsak':
                                    keterangan = "waktu"
                                else:
                                    keterangan = "sholat"

                                if k == 'terbit':t = datetime.datetime.strptime(v,'%H:%M')
                                if k == 'maghrib':m = datetime.datetime.strptime(v,"%H:%M")
                                if hari == "Fri" and k == "dzuhur":                                    
                                    sholat = "jumat"
                                else:
                                    sholat = k                                
                                if jam < v:                                    
                                    status = ""
                                    sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                            waktu, chat_id, chat_type, user_id, user_name, keterangan, 0,sholat,nama)                            
                                    cur.execute(sql)
                                    db.commit()
                                else:
                                    status = (kamus("sholat_lewat"))
                                jadwal.append('%s %s %s'%(v,sholat,status))
                        tahajud = (t-((m-t)/3)).strftime("%H:%M")
                        if jam < tahajud:
                            status = ""
                            waktu_tahajud = '%s %s:00'%(tanggal,tahajud)
                            sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                   waktu_tahajud, chat_id, chat_type, user_id, user_name, "sholat", 0,"tahajud",nama)                            
                            cur.execute(sql)
                            db.commit()
                        else:
                            status = (kamus("sholat_lewat"))
                        jadwal.append('%s %s %s'%(tahajud,'tahajud',status))
                        jadwal.sort()
                        agenda_sholat =''.join('%s \n'%jadwal[i] for i in range(len(jadwal)))
                        update.message.reply_text(str(kamus("sholat_jadwal"))%(nama,tanggal,agenda_sholat))
                        break
                    elif re.search(f"{nama}", a['nama'], re.IGNORECASE):
                        mirip.append(f"`{escape_markdown(a['nama'])}`")
                else:
                    # update.message.reply_text(kamus("kota_tidak_ketemu")%url_kota)
                    pesan = kamus("kota_ketemu_sebagian")%"\n- ".join(mirip) if len(mirip)>0 else kamus("kota_tidak_ketemu")%url_kota
                    update.message.reply_text(pesan,parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(str(kamus("sholat_sudah_setting")%nama))
        except Exception as e:     
                   
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))

    def restart_pull(self, update, context):
        user_id = update.message.from_user.id
        if user_id not in [582005141, 377596941]:
            update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan perintah ini.")
            return
    
        try:
            message = update.message.reply_text("🔄 Memeriksa pembaruan dari GitHub...")
            
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, 
                                         text=True)
            if status_result.stdout.strip():
                message.edit_text("❌ Direktori kerja tidak bersih. Harap commit atau stash perubahan terlebih dahulu.")
                return
            
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, 
                                         text=True)
            current_branch = branch_result.stdout.strip()
            
            pull_result = subprocess.run(['git', 'pull', 'origin', current_branch], 
                                       capture_output=True, 
                                       text=True)
            
            if pull_result.returncode != 0:
                message.edit_text(
                    f"❌ Gagal melakukan git pull:\n\n{pull_result.stderr}", 
                    parse_mode='Markdown'
                )
                return
            
            if "Already up to date" in pull_result.stdout:
                message.edit_text("ℹ️ Tidak ada pembaruan baru yang tersedia.")
                return
                
            with open('/tmp/bot_restart_info.json', 'w') as f:
                json.dump({'chat_id': chat_id}, f)
            
            message.edit_text(
                f"✅ Pembaruan berhasil!\n"
                f"Branch: `{current_branch}`\n"
                f"\n{pull_result.stdout}\n"
                "🔄 Memulai ulang bot...",
                parse_mode='Markdown'
            )
            
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        except Exception as e:
            update.message.reply_text(
                f"❌ Terjadi kesalahan saat pembaruan/restart:\n\n{str(e)}",
                parse_mode='Markdown'
            )
        
    def set_timer(self,update,context):
        args = context.args
        if args[0].upper() == 'SHOLAT':
            try:
                kota = ' '.join(args[1:]).upper()                
                self.jadwal_sholat(update,context,kota)
            except:
                self.help(update,context)
        else:            
            try:        
                huruf = ''
                try:
                    angka   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(1)
                    huruf   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(2)
                except:
                    angka   = args[0]
                    satuan  = 1

                if huruf == 's' or huruf == 'd' or huruf == '':
                    satuan  = 1
                elif huruf == 'm':
                    satuan  = 60
                elif huruf == 'h' or huruf == 'j':
                    satuan  = 3600
                else:
                    update.message.reply_text(kamus("cmd_salah"))
                    return

                self.hitung(update,context,args,int(angka)*satuan)
            except (IndexError, ValueError):
                self.set_jam(update,context, args)

    def hitung(self,update,context,args,due):
        try:
            z       = self.t1.is_alive()
            
            chat_id = update.message.chat_id
            if due <= 0:
                update.message.reply_text(kamus("jadwal_lewat"))                
                return
            
            pesan = ' '.join(update.message.text.split(" ")[2:])
            # match = re.match(r'^[A-Za-z0-9 ?!\/&,.:@]*$', pesan )
            # if match :
            sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
            waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=due,hours=0))
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user['first_name']
            
            sql         = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES (?,?,?,?,?,?,?,'','')"
            cur.execute(sql,(waktu, chat_id, chat_type, user_id, user_name, pesan, 0))
            db.commit()                
            update.message.reply_text(kamus("jadwal_set")%(sekarang, waktu))
            # else:
            #     update.message.reply_text('incorrect string')
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))

    def agenda(self,update,context):
        try:
            z       = self.t1.is_alive()
            user_id = update.message.from_user.id
            chat_id = update.message["chat"]["id"]
            sql     = "SELECT waktu, pesan, sholat, kota FROM daftar_timer WHERE user_id = '%s' AND chat_id = '%s' AND done = 0"%(user_id, chat_id)
            bar, jum = eksekusi(sql)

            if jum == 0:
                update.message.reply_text(kamus("jadwal_kosong"))
            else:
                cek = []
                for i in range(jum):
                    waktu       = bar[i][0]                    
                    sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:
                        teks    = kamus("sholat_lewat")
                        done    = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,chat_id,user_id)
                        cur.execute(done)
                        db.commit()
                    else:
                        teks    = ""
                    cek.append("%s %s %s %s %s"%(waktu, bar[i][1],bar[i][2],bar[i][3], teks))                    
                cek.sort()
                agenda  = ''.join('%s \n'%cek[i] for i in range(len(cek)))
                update.message.reply_text(kamus("jadwal_list")%agenda)
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))
    
    # def error(self,update,context):
    #     """Log Errors caused by Updates."""
    #     logger.warning('Update "%s" caused error "%s"', update, context.error)

    
    def timer(self):
        while True:           
            sekarang    = datetime.datetime.now()
            hari        = datetime.datetime.strftime(sekarang.date(),"%a") 
            waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang+datetime.timedelta(seconds = 0, hours=0))
            sql         = "SELECT waktu, pesan, chat_id, user_name, sholat, kota, user_id FROM daftar_timer WHERE waktu = '%s'"%waktu
            sql_corona  = "SELECT waktu, area, chat_id, positif, sembuh, meninggal, waktu_berikutnya FROM kawalCoronaSub WHERE  langganan = 1"
            # self.timer_corona(Update, CallbackContext, sql = sql_corona, waktu = waktu, sekarang = sekarang)
            self.timer_sholat(Update, CallbackContext, sql = sql, hari = hari, waktu = waktu)
            
            waktuBackup = '{:%H:%M:%S}'.format(datetime.datetime.now())
            if (str(waktuBackup) == '18:00:00'):
                self.set_backup()
            
            time.sleep(1)            
            
    def timer_sholat(self,update:Update,context,sql, hari, waktu):
        bot         = Bot(token = Config.TOKEN)
        bar, jum = self.eksekusi(sql)
        if jum != 0:
            for i in range(jum):
                # barWaktu       = bar[i][0]
                barPesan       = bar[i][1]
                barChat_id     = bar[i][2]
                barUser_name   = bar[i][3]
                barSholat      = bar[i][4]
                barKota        = bar[i][5]
                barUser_id     = bar[i][6]
                if len(barSholat) > 1:
                    if barPesan== 'sholat':
                        kata = "\n\n%s"%kamus("sholat_footnote")
                    else:
                        kata = ""
                    if hari == "Sun":
                        sholat_waktu = barPesan
                        if sholat_waktu == "waktu":
                            sholat_waktu = "time"
                        else:
                            sholat_waktu = "prayer"
                        
                        if barSholat == "terbit":
                            sholat = "sunrise"
                        else:
                            sholat = barSholat
                        pesan = (kamus("sholat_teks")%(sholat,sholat_waktu, barKota, barUser_name,kata))
                    else:
                        pesan = (kamus("sholat_teks")%(barPesan, barSholat, barKota, barUser_name,kata))
                else:
                    if (barPesan.split()[0])=="banned":                                
                        try:
                            user_id = (barPesan.split()[1])
                            bot.send_sticker(barChat_id, 'CAADBQADSQ4AAs_rwQcgxkK2JzKWwhYE')  # banhammer marie sticker
                            bot.kick_chat_member(barChat_id, user_id)
                            pesan = ("banned [%s](tg://user?id=%s)"%(barUser_name,user_id))
                        except Exception as e:                            
                            pesan = ("ane gagal %s - [%s](tg://user?id=%s)"%(barPesan,barUser_name, barUser_id))
                            bot.send_sticker(barChat_id, 'CAACAgUAAxkBAAIVY18FFska2MmU5E4nPNco6m0RTRQhAALaAAM_5Bom20PZpUJeLM8aBA')  # banhammer marie sticker
                            done = "UPDATE new_members SET done = 1, age = '%s' WHERE chat_id = '%s' AND user_id = '%s'"%(0, barChat_id, barUser_id)
                            self.cur.execute(done)
                            self.db.commit()
                    else:
                        pesan = ("%s - [%s](tg://user?id=%s)"%(barPesan,barUser_name,barUser_id))
                
                try:
                    bot.send_message(text = pesan,chat_id = barChat_id,parse_mode=ParseMode.MARKDOWN)
                except:
                    bot.send_message(text = pesan,chat_id = barChat_id)
                done = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s'"%(waktu, barChat_id)
                self.cur.execute(done)
                self.db.commit()
                del barPesan, barUser_name, barSholat, barKota        

    def timer_corona(self,update,context,sql, waktu, sekarang):    
        bot         = Bot(token = Config.TOKEN)
        barCor,jumCor = eksekusi(sql)
        if jumCor != 0:            
            for i in range(jumCor):                
                cek_date = barCor[i][6]                        
                if cek_date > waktu:
                    pass
                elif cek_date < waktu:
                    # menghitung ulang saat waktu nya kelewat
                    berikutnya  = sekarang+datetime.timedelta(seconds = 300, hours=0)
                    berikutnya  = '{:%Y-%m-%d %H:%M:%S}'.format(berikutnya)    
                    chat_id     = barCor[i][2]
                    provinsi    = barCor[i][1]
                    sql_update  = "UPDATE kawalCoronaSub SET waktu_berikutnya=? WHERE chat_id = ? AND area = ? AND langganan = 1"
                    arg_update  = (berikutnya,chat_id,provinsi)
                    cur.execute(sql_update,arg_update)
                    db.commit()
                else:
                    try:                    
                        total_lama  = barCor[i][3]+barCor[i][4]+barCor[i][5]
                        chat_id     = barCor[i][2]
                        provinsi    = barCor[i][1]                                  
                        kode, tampil, positif, sembuh, meninggal  = kawalCorona.stat_corona(update,context,provinsi,chat_id)
                        pesan       = kawalCorona.corGraph(update,context,provinsi,chat_id)                                
                        total_baru  = int(positif)+int(sembuh)+int(meninggal)
                        if int(positif) - barCor[i][3]>0:
                            selisih_positif = "+%s"%(int(positif)-barCor[i][3])
                        else:
                            selisih_positif = "-%s"%(barCor[i][3]-int(positif))

                        if int(sembuh) - barCor[i][4]>0:
                            selisih_sembuh = "+%s"%(int(sembuh)-barCor[i][4])
                        else:
                            selisih_sembuh = "-%s"%(barCor[i][4]-int(sembuh))

                        if int(meninggal) - barCor[i][5]>0:
                            selisih_meninggal = "+%s"%(int(meninggal)-barCor[i][5])
                        else:
                            selisih_meninggal = "-%s"%(barCor[i][5]-int(meninggal))

                        tampil.append("``` Data sebelumnya %s\n Positif\t\t: %s\t\t%s\n Sembuh\t\t\t: %s\t\t%s\n Meninggal: %s\t\t%s```"%(barCor[i][0], barCor[i][3], selisih_positif,barCor[i][4],selisih_sembuh,barCor[i][5],selisih_meninggal))
                        if total_lama != total_baru:
                            tampil = (''.join('%s \n'%tampil[j] for j in range(len(tampil))))
                            if pesan:
                                filename= "%s%s"%(provinsi,chat_id)
                                file    = open("%s.png"%filename,"rb")
                                bot.sendPhoto(chat_id=chat_id, photo=file, caption=tampil, parse_mode = ParseMode.MARKDOWN)
                            else:
                                bot.send_message(text = tampil,chat_id = chat_id,parse_mode=ParseMode.MARKDOWN)
                            sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang)
                            sqlStat     = "INSERT INTO kawalCorona (tanggal, chat_id,area,positif,sembuh,meninggal) VALUES (?,?,?,?,?,?)"
                            argStat     = (sekarang,chat_id,provinsi, positif, sembuh, meninggal)
                            cur.execute(sqlStat, argStat)
                            db.commit()
                    except:
                        pass
                del cek_date

    def set_backup(self):
        bot         = Bot(token = Config.TOKEN)
        src = sqlite3.connect('database')
        dst = sqlite3.connect('backup.db')
        with dst:
            src.backup(dst, pages=1)
        dst.close()
        src.close()

        now     = datetime.datetime.now()
        tanggal = now.strftime("%d%m%Y-%H%M%S")
        namaFile= f"sarbot{tanggal}.tar.gz"
        tar     = tarfile.open(namaFile, "w:gz")
        chatId  = -1001337729941

        for root, dirs, files in os.walk(os.getcwd()):
            for name in files:
                if (name.endswith((".py",".py")) or name == 'database'):
                    tar.add(os.path.join(root, name))
        tar.close()


        file = open(namaFile,"rb")
        bot.send_document(chatId, file)

    def koneksiDatabase(self):
        self.db          = sqlite3.connect(pathDB, check_same_thread = False)
        self.cur         = db.cursor()

    def eksekusi(self, sql):
        self.cur.execute(sql)
        self.db.commit()
        lineData = self.cur.fetchall()
        totData  = len(lineData)
        return lineData, totData


if __name__ == '__main__':
    bot_timer()
