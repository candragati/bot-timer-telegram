#credit : https://github.com/Billal06/KawalCorona

from config import *
from telegram import ParseMode
from telegram import MessageEntity
import requests
import time
import datetime 
import threading
import random
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import pygal
from pygal.style import NeonStyle


# lock = threading.Lock()
detik = 300
def cor(update,context):
    data1       = []
    data2       = []
    tampil      = []
    negara      = "indonesia"
    url_utama   = "https://api.kawalcorona.com/"
    url_prov    = "https://api.kawalcorona.com/indonesia/provinsi"
    m           = update.effective_message
    chat_id     = update.message["chat"]["id"]
    chat_type   = update.message["chat"]["type"]
    teks        = context.args    
    
    if (len(teks))==0:
        update.message.reply_text("Silahkan tulis nama provinsinya")
        return
    if teks[0].lower() == "sub":  
        provinsi = ' '.join(teks[1:])
        kode, tampil,positif,sembuh,meninggal = stat_corona(update,context,provinsi)
        if kode == 1:
            cek = "SELECT area,langganan FROM kawalCoronaSub WHERE chat_id = ? AND area = ?"
            arg = (chat_id,provinsi)
            bar, jum = eksekusi(cek,arg)            
            if jum ==0:
                sekarang    = datetime.datetime.now()    
                berikutnya  = sekarang+datetime.timedelta(seconds = detik, hours=0)
                sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang)
                berikutnya  = '{:%Y-%m-%d %H:%M:%S}'.format(berikutnya)
                sql         = "INSERT INTO kawalCoronaSub (waktu, chat_id,chat_type,area,positif,sembuh,meninggal,langganan,waktu_berikutnya,done) VALUES (?,?,?,?,?,?,?,?,?,?)"
                arg         = (sekarang,chat_id,chat_type,provinsi,positif,sembuh,meninggal,1,berikutnya,0)
                eksekusi(sql,arg)                
                tampil.append("Jumlah pasien korona area %s akan di laporkan berkala"%provinsi)
            elif bar[0][1]==0:
                sekarang    = datetime.datetime.now()    
                berikutnya  = sekarang+datetime.timedelta(seconds = detik, hours=0)
                sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang)
                berikutnya  = '{:%Y-%m-%d %H:%M:%S}'.format(berikutnya)
                sql         = "UPDATE kawalCoronaSub SET waktu=?, positif=?,sembuh=?,meninggal=?,langganan=?,waktu_berikutnya=?,done=? WHERE chat_id = ? AND area = ?"
                arg         = (sekarang,positif,sembuh,meninggal,1,berikutnya,0,chat_id,provinsi)
                eksekusi(sql,arg)
                
                tampil.append("Jumlah pasien korona area %s akan di laporkan berkala"%provinsi)
            else:
                tampil.append("Disini sudah berlangganan statistik corona area %s"%provinsi)
    elif teks[0].lower() == "unsub":
        provinsi = ' '.join(teks[1:])
        kode, tampil,positif,sembuh,meninggal = stat_corona(update,context,provinsi)
        if kode == 1:
            cek = "SELECT area,langganan FROM kawalCoronaSub WHERE chat_id = ? AND area = ?"
            arg = (chat_id,provinsi)
            bar, jum = eksekusi(cek,arg)
            if jum !=0 and bar[0][1] ==1:
                sql = "UPDATE kawalCoronaSub SET langganan = 0 WHERE chat_id = ? AND area = ?"
                arg = (chat_id,provinsi)
                eksekusi(sql,arg)
                
                tampil.append("Anda tidak lagi menerima laporan jumlah pasien korona area %s disini"%provinsi)        
    else:
        provinsi = ' '.join(teks)
        kode, tampil,positif,sembuh,meninggal  = stat_corona(update,context,provinsi)
    update.message.reply_text(''.join('%s \n'%tampil[i] for i in range(len(tampil))),parse_mode=ParseMode.MARKDOWN)            
        
def stat_corona(update,context,args,chat_id = None):
    data1       = []
    data2       = []
    tampil      = []
    positif     = 0
    sembuh      = 0
    meninggal   = 0
    negara      = "indonesia"
    url_utama   = "https://api.kawalcorona.com/"
    url_prov    = "https://api.kawalcorona.com/indonesia/provinsi"
    teks        =  context.args
    try:
        if teks[0].lower() == "sub" or teks[0].lower() == "unsub":
            provinsi = ' '.join(teks[1:])
        else:
            provinsi = ' '.join(teks)            
    except:
        provinsi =  args
    
    # req=requests.get(url_utama).json()    
    # for x in req:
    #     data1.append(x['attributes'])
    # for a in data1:
    #     country = a["Country_Region"]
    #     if negara.lower() in country.lower():
    #         tampil.append("Last Update "+time.ctime(int(str(a["Last_Update"])[:-3])))        

    list_prov = []
    req=requests.get(url_prov).json()
    for x in req:
        data2.append(x['attributes'])

    for a in data2:
        list_prov.append(a['Provinsi'].lower())
    
    try:
        sekarang    = datetime.datetime.now()    
        berikutnya  = sekarang+datetime.timedelta(seconds = detik, hours=0)
        sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang)
        berikutnya  = '{:%Y-%m-%d %H:%M:%S}'.format(berikutnya)    
        list_prov.index(provinsi)
        for a in data2:
            prov = a["Provinsi"]        
            if provinsi.lower() in prov.lower():
                positif     = str(a['Kasus_Posi'])
                sembuh      = str(a['Kasus_Semb'])
                meninggal   = str(a['Kasus_Meni'])
                tampil.append("``` Provinsi\t: %s\n Positif\t\t: %s\n Sembuh\t\t\t: %s\n Meninggal: %s```"%(prov,positif,sembuh,meninggal))
        kode = 1
        if chat_id != None:
            sql = "UPDATE kawalCoronaSub SET waktu = ?,positif = ?, sembuh = ?,meninggal = ?,waktu_berikutnya=? WHERE chat_id = ? AND area = ?"
            arg = (sekarang,positif,sembuh,meninggal,berikutnya,chat_id,provinsi)
            eksekusi(sql,arg)
            
            

    except Exception as e:
        tampil.append("Provinsi %s tidak ketemu"%provinsi)
        kode = 0
    return kode,tampil,positif,sembuh,meninggal

def corGraph(update,context,args=None,chat_id = None):  
    if args == None:
        teks        =  context.args
        try:
            provinsi = ' '.join(teks)            
        except:
            provinsi =  args
    else:
        provinsi = args

    if chat_id == None:
        chat_id     = update.message["chat"]["id"]
    
    filename = "%s%s"%(provinsi,chat_id)
    sql = "SELECT positif, sembuh, meninggal,strftime('%Y-%m-%d',tanggal) FROM kawalCorona WHERE chat_id = ? AND area = ? group by strftime('%Y-%m-%d',tanggal)"
    arg = (chat_id,provinsi)
    bar, jum = eksekusi(sql,arg)        
    if jum == 0:
        if args == None:
            update.message.reply_text('Saya mau aja nampilin data, tapi datanya justru yang gak ada.')
        else:
            return 0
    else:
        positif     = []
        sembuh      = []
        meninggal   = []
        tanggal     = []
        bulan       = []
        for i in range(jum):
            # print (bar[i][3],bar[i][0],bar[i][1],bar[i][2])
            positif.append(bar[i][0])
            sembuh.append(bar[i][1])
            meninggal.append(bar[i][2])
            tanggal.append((datetime.datetime.strptime(bar[i][3],'%Y-%m-%d').strftime("%d")))
            bulan.append((datetime.datetime.strptime(bar[i][3],'%Y-%m-%d').strftime("%b")))
            
        
        judul_x = "Bulan: %s"%' '.join(bulan[i] for i in range(len(list(set(bulan)))))
        chart = pygal.Line(
            stroke_style        = {'width':2},
            fill                = True,
            style               = NeonStyle, 
            show_y_guides       = True,
            show_x_guides       = True,
            x_label_rotation    = -90,
            interpolate         = 'cubic', 
            x_title             = judul_x,
            title               = provinsi.upper(),
            width               = 600,
            height              = 400)
        chart.x_labels = tanggal
        chart.add('positif', positif)
        chart.add('sembuh', sembuh)
        chart.add('meninggal', meninggal)
        chart.render_to_file('%s.svg'%filename)
        drawing = svg2rlg("%s.svg"%filename)
        renderPM.drawToFile(drawing, "%s.png"%filename, fmt="PNG")
        if args == None:
            kode, tampil,positif,sembuh,meninggal  = stat_corona(update,context,provinsi)
            file = open("%s.png"%filename,"rb")
            context.bot.sendPhoto(chat_id=chat_id, photo=file, caption=tampil[0], parse_mode = ParseMode.MARKDOWN)
        else:
            return 1
        
