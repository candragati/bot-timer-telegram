# Tue Jan  1 01:52:50 2019 sort jadwal
# Tue Jan  8 03:01:55 2019 qotd simpan forward quote
# Wed Jan  9 20:55:01 2019 set bio, afk, dan me
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import MessageEntity
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
import logging
import datetime
import re
import sqlite3
import time
# import _thread
import threading
import requests
import random
from config import *
from modul import me,bio


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

class bot_timer():
    def __init__(self):
        self.koneksiDatabase()
        updater = Updater(Config.TOKEN)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("afk", self.set_afk))
        dp.add_handler(CommandHandler("setbio", bio.set_bio))
        dp.add_handler(CommandHandler("bio", bio.bio))
        dp.add_handler(CommandHandler("setme", me.set_me))
        dp.add_handler(CommandHandler("me", me.me))
        dp.add_handler(CommandHandler("qotd", self.qotd, pass_args = True))
        dp.add_handler(CommandHandler("dqotd", self.dqotd, pass_args = True))
        dp.add_handler(CommandHandler("rqotd", self.rqotd))
        dp.add_handler(CommandHandler("help", self.help))
        dp.add_handler(CommandHandler("agenda", self.agenda))
        dp.add_handler(CommandHandler("set", self.set_timer,
                                      pass_args=True,
                                      pass_job_queue=True,
                                      pass_chat_data=True))
        dp.add_handler(CommandHandler("hitung", self.timer,pass_chat_data = True, pass_job_queue = True, pass_args = True))
        dp.add_handler(MessageHandler(Filters.text, self.echo_afk))
        dp.add_error_handler(self.error)
        # Start the Bot
        updater.start_polling()
        updater.idle()

    def echo_afk(self,bot, update):
        #sudah nongol
        chat_id = update.message["chat"]["id"]
        from_user_name = update.message.from_user.username
        from_user_id = update.message.from_user.id
        cek = "SELECT user_name FROM afk WHERE chat_id='%s' AND user_id='%s' AND hapus = 0"%(chat_id, from_user_id)
        bar, jum = self.eksekusi(cek)
        if jum ==0:
            pass
        else:
            sql = "UPDATE afk SET hapus = 1 WHERE chat_id = ? AND user_id = ?"
            self.cur.execute(sql,(chat_id,from_user_id))
            self.db.commit()
            update.message.reply_text("%s sudah nongol lagi"%from_user_name)
    
        # Dari mention
        message = update.effective_message
        entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
        if message.entities and entities:
            for ent in entities:
                if ent.type == MessageEntity.TEXT_MENTION:
                    user_id = ent.user.id                    

                elif ent.type == MessageEntity.MENTION:
                    user_id = (message.text[ent.offset:ent.offset + ent.length])
                    if not user_id:
                        return
                    mention = user_id.replace("@","")
                    cek = "SELECT user_name,teks FROM afk WHERE chat_id='%s' AND user_name='%s' AND hapus = 0"%(chat_id, mention)
                    bar, jum = self.eksekusi(cek)
                    if jum == 0:
                        pass
                    else:
                        update.message.reply_text("%s gak online, dia lagi %s"%(bar[0][0],bar[0][1]))
                else:
                    return

        # Dari reply
        try:
            r_user_name   =  message.reply_to_message.from_user.username
            cek = "SELECT user_name,teks FROM afk WHERE chat_id='%s' AND user_name='%s' AND hapus = 0"%(chat_id, r_user_name)
            bar, jum = self.eksekusi(cek)
            if jum == 0:
                pass
            else:
                update.message.reply_text("%s gak online, dia lagi %s"%(bar[0][0],bar[0][1]))
        except:
            pass

    def set_afk(self,bot,update):
        m = update.effective_message            
        teks =  m.text.split(None,1)
        if len(teks) == 2:        
            try:
                chat_id = str(update.message["chat"]["id"])
                chat_type = update.message["chat"]["type"]
                user_id = str(update.message.from_user.id)
                user_name = update.message.from_user.username
                cek = "SELECT user_name,teks FROM afk WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
                bar, jum = self.eksekusi(cek)
                if jum == 0:            
                    sql = "INSERT INTO afk (chat_id, chat_type, user_id, user_name, teks,hapus) VALUES (?,?,?,?,?,0)"
                    self.cur.execute(sql,(chat_id, chat_type, user_id, user_name, teks[1]))
                else:
                    sql = "UPDATE afk SET teks = ?, hapus = ? WHERE chat_id = ? AND user_id = ?"
                    self.cur.execute(sql,(teks[1],'0',chat_id,user_id))
                self.db.commit()
                update.message.reply_text("%s sekarang AFK"%user_name)
            except Exception as e:
                update.message.reply_text("ketik /afk <alasan anda>\n%s"%e)
                
    def qotd(self,bot,update, args):
        chat_id = update.message["chat"]["id"]                
        if len(args)==0:
            m = update.effective_message            
            try:
                waktu = str(m.reply_to_message.date.strftime('%Y-%m-%d %H:%M:%S'))
                quote =  m.reply_to_message.text.replace("'","''")
                cek = "SELECT nomor FROM qotd WHERE quote = '%s'"%(quote)
                barC,jumC = self.eksekusi(cek)
                if jumC >= 1:
                    update.message.reply_text(str(self.kamus("qotd_dobel"))%(barC[0][0]))
                else:
                    try:
                        user_name   =  update.message["reply_to_message"]["forward_from"]["username"]
                        user_id     =  update.message["reply_to_message"]["forward_from"]["id"]
                    except:                        
                        user_name   =  m.reply_to_message.from_user.username
                        user_id     =  m.reply_to_message.from_user.id
                    chat_type = update.message["chat"]["type"]
                    hitung = "SELECT quote FROM qotd WHERE chat_id = '%s'"%(chat_id)
                    bar, jum = self.eksekusi(hitung)            
                    jum = jum+1
                    sql = "INSERT INTO qotd (nomor,waktu, chat_id, chat_type, user_id, user_name, quote, hapus) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')"%(
                    jum,waktu, chat_id, chat_type, user_id, user_name, quote, 0)
                    self.cur.execute(sql)
                    self.db.commit()
                    update.message.reply_text(str(self.kamus("quote_simpan"))%(jum,jum,jum))
            except Exception as e:            
                update.message.reply_text('%s\n%s'%(self.kamus("quote_mogok"),e))
        elif str(args[0]).isdigit():
            sql = "SELECT quote, user_name, nomor FROM qotd WHERE chat_id = '%s' AND nomor = '%s'"%(chat_id, args[0])
            bar, jum = self.eksekusi(sql)
            if jum == 0:
                update.message.reply_text(self.kamus("quote_not_found"))
            else:
                update.message.reply_html("<i>{}</i>\n\n@{}:{}".format(bar[0][0],bar[0][1],bar[0][2]))
        else:
            update.message.reply_text("Silahkan reply atau forward chat yang akan di quote")

    def rqotd(self,bot,update):
        chat_id = update.message["chat"]["id"]
        quote = []
        sql = "SELECT quote, user_name,nomor FROM qotd WHERE chat_id = '%s' AND hapus = 0"%chat_id
        bar, jum = self.eksekusi(sql)
        for i in range(jum):
            quote.append("<i>{}</i>\n\n@{}:{}".format(bar[i][0],bar[i][1],bar[i][2]))        
        update.message.reply_html(random.choice(quote))

    def dqotd(self,bot, update, args):
        chat_id = update.message["chat"]["id"]
        if len(args) == 0:
            update.message.reply_text(self.kamus("quote_kurang"))
        elif str(args[0]).isdigit():
            hitung = "SELECT quote FROM qotd WHERE chat_id = '%s'"%(chat_id)
            bar, jum = self.eksekusi(hitung)            
            if jum == 0:
                update.message.reply_text(self.kamus("dqotd_not_found"))
            else:
                sql = ("UPDATE qotd SET hapus = 1 WHERE chat_id = '%s' AND nomor = '%s'"%(chat_id, args[0]))
                self.cur.execute(sql)
                self.db.commit()                
                update.message.reply_text(self.kamus("dqotd_sukses"))
        else:
            update.message.reply_text(self.kamus("quote_kurang"))
        

    def kamus(self,teks):
        a = {
            "qotd_mogok":{
                "id":   ["Silahkan reply atau forward chat yang akan di quote"],
                "en":   ["Please reply or forward a quotable chat."],
            },
            "qotd_dobel":{
                "id":   ["Dobel quote dengan ID nomor %s"],
                "en":   ["Duplicate quote with ID %s"]
            },
            "dqotd_sukses":{
                "id":   ["Berhasil di dequote"],
                "en":   ["dequote success!"],                
            },
            "dqotd_not_found":{
                "id":   ["Kok ID nya gak ada ya? Yakin udah bener?"],
                "en":   ["ID not found"],
            },
            "quote_kurang":{
                "id":   ["Silahkan tambahin dengan ID nya."],
                "en":   ["Please add it with ID"]
            },
            "quote_not_found":{
                "id":   ["ID nya gak ketemu. Mungkin sudah dihapus atau udah mentok."],
                "en":   ["ID not found"]
            },
            "quote_mogok":{
                "id":   ["Gak bisa simpen quote, liat errornya di bawah ini"],
                "en":   ["Cannot saved quote. See error below."]
            },
            "quote_simpan":{
                "id":   ["Quote disimpan dengan id %s\nuntuk lihat, ketik /qotd %s\nuntuk dequote, ketik /dqotd %s"],
                "en":   ["Quote saved with id %s\nto see quote : /qotd %s\nto dequote : /dqotd %s"]
            },
            "mogok":   {
                "id":  [
                    "Saya mogok, silahkan /start dulu.",
                    "Saya mogok, biasanya sih habis mati lampu belum di /start lagi.",
                    "Saya mogok, /start nya dipencet dulu dong.",
                    "lagi maintenance dulu, pencet /start ya"],
                "en":  ["I cant run, please /start"]
            },

            "sholat_footnote":   {
                "id":  [
                    "Berwudhu di jam sekarang, selain seger, juga bikin hati dan pikiran lebih tenang pak.",
                    "Dengan sholat tepat waktu, semoga doa kita juga semakin cepat di dengar olehNya",
                    "Alhamdulillah masih diberi kesempatan untuk beribadah, sholat yuk",
                    "Mari tinggalkan duniawi sesaat, untuk masa depan kita di akhirat.",
                    "Istirahat dulu pak, ambil air wudhu",
                    "Sholat itu gak nyita waktu kok, cuma sebentar doang",
                    "Jangan sampai Allah berpaling sama kita karena waktu sholat aja kita gak peduli",
                    "Jangan mau ikuti bisikan setan untuk ngulur2 waktu sholat pak",
                    "'Ya Rasulullah, amalan apa yang paling utama?'\n'Shalat tepat pada waktunya'\n(HR.Bukhari)",
                    "Jagalah sholatmu, ketika ketika kau kehilangannya, kau akan kehilangan yang lainnya\n(Umar bin Khattab)",
                    "Ketahuilah, hanya dengan mengingat Allah, hati akan menjadi tentram\n(Ar-Ra'd ayat:28)",
                    "Kalau hidupmu tidak jadikan sholat sebagai penghapus dosa, maka dosa akan menghapus sholat dalam hidupmu",
                    "Yuk benahi sholat wajib, dan amalkan sholat sunnah",
                    "'dan tiadalah kehidupan di dunia ini, kecuali permainan dan kesenangan belaka.'\n(Al An'Am:32)",
                    "Perbaikilah sholatmu. Amalan yang lain akan menjadi baik\n(HR.Ath-Thabarani)",
                    "Ya Allah, sesungguhnya aku mohon kepadaMu husnul khotimah",
                    "Ya Allah, berilah hamba rezeki berupa taubat nasuhah sebelum mati",
                    "Ya Allah, yang Maha membulak-balikkan hati, tetapkanlah hatiku di atas agamaMu",
                    "Barangsiapa bertakwa kepada Allah, niscaya Dia akan mengadakan baginya jalan keluar, dan memberinya rizki dari arah yang tidak disangka-sangkanya\n(QS Ath-Thalaq:2-3)",
                    "Setiap anak Adam bersalah. Dan sebaik-baiknya orang yang bersalah adalah orang-orang yang bertaubat",
                    "Orang yang ikhlas itu seperti orang yang berjalan di atas pasir. Kita tidak mendengar suaranya, namun melihat bekasnya.\n(Ibnu Mas'ud)"
                    ],
                "en":  [
                    "Don't wait for six strong men to take you to the mosque",                    
                    "Worries end when sholat begins",
                    "Ya Allah, I am lost. Bring me back to You",
                    "Alhamdulillah for everything that happens to me, happy or sad",
                    "Do not fear, I am with you, I hear and I See \n-Allah",
                    "Do not lose hope, nor be sad\n(Quran 3:139)"
                    ]
            },

            "cmd_start":   {
                "id":  ["Saya siap menghitung\npake /set <detik> <pesan> untuk timer"],
                "en":  ["Ready to count\nuse /set <second> <message> for timer"]
            },

            "cmd_help":   {
                "id":  ["/set <detik> <pesan> untuk timer\n/set sholat <kota> untuk set jadwal sholat\n/agenda untuk liat timer yang belum dieksekusi\n\ns atau d = untuk detik\nm = untuk menit\nh atau j = untuk jam"],
                "en":  ["/set <second> <message> for timer\n/set sholat <city> for set the schedule of prayers\n/agenda to see current timer\n\ns or d = for second\nm = for minute\nh or j = for hour"]
            },

            "cmd_error":   {
                "id":  ["perintah: /set <detik> <pesan>"],
                "en":  ["command: /set <second> <message>"]
            },

            "cmd_salah":   {
                "id":  ["format salah. \ns atau d = untuk detik\nm = untuk menit\nh atau j = untuk jam"],
                "en":  ["Bad command. \ns or d = for second\nm = for minute\nh or j = for hour"]
            },

            "id_ketemu":   {
                "id":  ["ketemu dengan id : %s"],
                "en":  ["find with id : %s"]
            },

            "kota_tidak_ketemu":   {
                "id":  ["kota tidak ketemu.\nCek daftar kota di %s "],
                "en":  ["city not found.\nPlease check your city ID at %s"]
            },

            "sholat_lewat":   {
                "id":  ["-> sudah kelewat"],
                "en":  ["-> already over"]
            },

            "sholat_jadwal":   {
                "id":  ["Jadwal sholat untuk wilayah %s\ntanggal %s\n\n%s"],
                "en":  ["prayer schedule for the region of %s\ndate %s\n\n%s"]
            },

            "sholat_sudah_setting":   {
                "id":  ["jadwal sholat wilayah %s sudah di setting per hari ini"],
                "en":  ["prayer schedule for the %s area have been set today"]
            },

            "jadwal_lewat":   {
                "id":  ["Maap. Waktu sudah kelewat, kita harus move on."],
                "en":  ["Time has passed."]
            },

            "jadwal_set":   {
                "id":  ["%s <- waktu saat ini\n%s <- Timer berhasil di set"],
                "en":  ["%s <- curent time\n%s <- timer set"]
            },

            "jadwal_kosong":   {
                "id":  ["Anda tidak memiliki agenda timer"],
                "en":  ["you dont have an agenda timer"]
            },

            "jadwal_list":   {
                "id":  ["Agenda anda saat ini adalah :\n\n%s"],
                "en":  ["Your current agenda :\n\n%s"]
            },

            "sholat_teks":   {
                "id":  ["saatnya %s %s untuk wilayah %s - @%s %s"],
                "en":  ["its %s %s for the %s region - @%s %s"]
            },
        }

        sekarang = datetime.datetime.now()
        hari = datetime.datetime.strftime(sekarang.date(),"%a")
        if hari == 'Sun':
            teks = random.choice(a[teks]['en'])
        else:
            teks = random.choice(a[teks]['id'])
        return teks

    def start(self,bot, update):
        try:
            z = self.t1.isAlive()
        except:            
            self.t1 = threading.Thread(target=self.timer, args=(bot,update))
            self.t1.start()
        # _thread.start_new_thread(self.timer,(bot,update))
        update.message.reply_text(self.kamus("cmd_start"))


    def help(self,bot, update):
        update.message.reply_text(self.kamus("cmd_help"))

    def set_tanggal(self,bot, update, args, job_queue, chat_data):
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime("%s %s"%(args[0], args[1]),"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            update.message.reply_text(self.kamus("cmd_error"))

    def set_jam(self,bot, update, args, job_queue, chat_data):
        now = '{:%Y-%m-%d}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime(now+" "+args[0],"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            self.set_tanggal(bot, update, args, job_queue, chat_data)

    def jadwal_sholat(self,bot,update, kota):
        try:
            z = self.t1.isAlive()
            nama = kota            
            sekarang = datetime.datetime.now()
            tanggal =  sekarang.strftime('%Y-%m-%d')
            jam =  sekarang.strftime('%H:%M')
            hari = datetime.datetime.strftime(sekarang.date(),"%a")
            chat_id = update.message["chat"]["id"]
            chat_type = update.message["chat"]["type"]
            user_id = update.message.from_user.id
            user_name = update.message.from_user.username
            cek = "SELECT waktu FROM daftar_timer WHERE kota = '%s' AND DATE(waktu) = '%s' AND chat_id = '%s'"%(nama,tanggal,chat_id)
            bar, jum = self.eksekusi(cek)
            if jum == 0:                
                url_kota = "https://api.banghasan.com/sholat/format/json/kota"
                r = requests.get(url_kota)
                kota_all  =  r.json()['kota']
                for a in kota_all:
                    if a['nama'] == nama.upper():
                        update.message.reply_text(str(self.kamus("id_ketemu"))%a['id'])
                        url = "https://api.banghasan.com/sholat/format/json/jadwal/kota/%s/tanggal/%s"%(a['id'],tanggal)            
                        r = requests.get(url)
                        sholat_all =  r.json()['jadwal']['data']
                        jadwal = []
                        t = ""
                        m = ""
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
                                    self.cur.execute(sql)
                                    self.db.commit()
                                else:
                                    status = (self.kamus("sholat_lewat"))
                                jadwal.append('%s %s %s'%(v,sholat,status))
                        tahajud = (t-((m-t)/3)).strftime("%H:%M")
                        if jam < tahajud:
                            status = ""
                            waktu_tahajud = '%s %s:00'%(tanggal,tahajud)
                            sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                   waktu_tahajud, chat_id, chat_type, user_id, user_name, "sholat", 0,"tahajud",nama)                            
                            self.cur.execute(sql)
                            self.db.commit()
                        else:
                            status = (self.kamus("sholat_lewat"))
                        jadwal.append('%s %s %s'%(tahajud,'tahajud',status))
                        jadwal.sort()
                        agenda_sholat =''.join('%s \n'%jadwal[i] for i in range(len(jadwal)))
                        update.message.reply_text(str(self.kamus("sholat_jadwal"))%(nama,tanggal,agenda_sholat))
                        break
                else:
                    update.message.reply_text(self.kamus("kota_tidak_ketemu")%url_kota)
            else:
                update.message.reply_text(str(self.kamus("sholat_sudah_setting")%nama))
        except Exception as e:            
            update.message.reply_text('%s\n%s'%(self.kamus("mogok"),e))

        
    def set_timer(self,bot, update, args, job_queue, chat_data):
        if args[0].upper() == 'SHOLAT':
            try:
                kota = ' '.join(args[1:]).upper()                
                self.jadwal_sholat(bot,update,kota)
            except:
                self.help(bot,update)
        else:            
            try:        
                huruf = ''
                try:
                    angka = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(1)
                    huruf = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(2)
                except:
                    angka = args[0]
                    satuan = 1

                if huruf == 's' or huruf == 'd' or huruf == '':
                    satuan = 1
                elif huruf == 'm':
                    satuan = 60
                elif huruf == 'h' or huruf == 'j':
                    satuan = 3600
                else:
                    update.message.reply_text(self.kamus("cmd_salah"))
                    return

                self.hitung(bot,update,args,job_queue, chat_data,int(angka)*satuan)
            except (IndexError, ValueError):
                self.set_jam(bot, update, args, job_queue, chat_data)

    def hitung(self,bot,update,args,job_queue, chat_data,due):
        try:
            z = self.t1.isAlive()
            chat_id = update.message.chat_id
            if due <= 0:
                update.message.reply_text(self.kamus("jadwal_lewat"))                
                return
            
            pesan = ' '.join(update.message.text.split(" ")[2:])
            match = re.match(r'^[A-Za-z0-9 ?!\/&,.:@]*$', pesan )
            if match :
                sekarang = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                waktu = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=due,hours=0))
                chat_id = update.message["chat"]["id"]
                chat_type = update.message["chat"]["type"]
                user_id = update.message.from_user.id
                user_name = update.message.from_user.username
                sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','','')"%(
                    waktu, chat_id, chat_type, user_id, user_name, pesan, 0)
                self.cur.execute(sql)
                self.db.commit()                
                update.message.reply_text(self.kamus("jadwal_set")%(sekarang, waktu))                
            else:
                update.message.reply_text('incorrect string')
        except Exception as e:
            update.message.reply_text('%s\n%s'%(self.kamus("mogok"),e))

    def agenda(self,bot,update):
        try:
            z = self.t1.isAlive()
            user_id = update.message.from_user.id
            chat_id = update.message["chat"]["id"]
            sql = "SELECT waktu, pesan, sholat, kota FROM daftar_timer WHERE user_id = '%s' AND chat_id = '%s' AND done = 0"%(user_id, chat_id)
            bar, jum = self.eksekusi(sql)

            if jum == 0:
                update.message.reply_text(self.kamus("jadwal_kosong"))
            else:
                cek = []
                for i in range(jum):
                    waktu = bar[i][0]                    
                    sekarang = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:
                        teks = self.kamus("sholat_lewat")
                        done = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,chat_id,user_id)
                        self.cur.execute(done)
                        self.db.commit()
                    else:
                        teks = ""
                    cek.append("%s %s %s %s %s"%(waktu, bar[i][1],bar[i][2],bar[i][3], teks))                    
                cek.sort()
                agenda =''.join('%s \n'%cek[i] for i in range(len(cek)))
                update.message.reply_text(self.kamus("jadwal_list")%agenda)
        except Exception as e:
            update.message.reply_text('%s\n%s'%(self.kamus("mogok"),e))
    
    def error(self,bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" menyebabkan terjadinya error "%s"', update, error)

    def koneksiDatabase(self):
        self.db = sqlite3.connect("database", check_same_thread = False)
        self.cur = self.db.cursor()

    def eksekusi(self,sql):
        self.cur.execute(sql)
        lineData = self.cur.fetchall()
        totData = len(lineData)
        return lineData, totData

    def timer(self,bot,update):
        while True:           
            sekarang = datetime.datetime.now()
            hari = datetime.datetime.strftime(sekarang.date(),"%a") 
            user_id = update.message.from_user.id
            waktu =  '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
            sql = "SELECT waktu, pesan, chat_id, user_name, sholat, kota FROM daftar_timer WHERE waktu = '%s'"%waktu
            # print (sql)
            try:
                bar, jum = self.eksekusi(sql)
                if jum ==0:
                    pass
                else:
                    for i in range(jum):
                        if len(bar[i][4]) > 1:
                            if bar[i][1]== 'sholat':
                                kata = "\n\n%s"%self.kamus("sholat_footnote")
                            else:
                                kata = ""
                            if hari == "Sun":
                                sholat_waktu = bar[i][1]
                                if sholat_waktu == "waktu":
                                    sholat_waktu = "time"
                                else:
                                    sholat_waktu = "prayer"
                                
                                if bar[i][4] == "terbit":
                                    sholat = "sunrise"
                                else:
                                    sholat = bar[i][4]
                                pesan = (self.kamus("sholat_teks")%(sholat,sholat_waktu, bar[i][5], bar[i][3],kata))
                            else:
                                pesan = (self.kamus("sholat_teks")%(bar[i][1], bar[i][4], bar[i][5], bar[i][3],kata))
                        else:
                            pesan = ("%s - @%s"%(bar[i][1],bar[i][3]))
                        bot.send_message(text = pesan,chat_id = bar[i][2])
                        done = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,bar[i][2],user_id)
                        self.cur.execute(done)
                        self.db.commit()
                time.sleep(1)
            except Exception as e:
                update.message.reply_text("Error %s"%e)

if __name__ == '__main__':
    bot_timer()
