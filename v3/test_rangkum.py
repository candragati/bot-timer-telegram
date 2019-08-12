from config import *
from reportKulgram import generate_commercial_invoice
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import inch

chat_id  = '-1001337729941'
sql = "SELECT nomor,waktu, judul, author  FROM rekam WHERE chat_id = '%s' AND done = 0"%chat_id
bar, jum = eksekusi(sql)
nomor =  bar[0][0]
waktu =  bar[0][1]
judul =  bar[0][2]
author =  bar[0][3]

header = {
                'chat_id'       : chat_id, 
                'no'        : nomor,
                'judul'          : judul,
                'author'          : author,
                'waktu'         : waktu,
                }

sql_rangkum = "SELECT waktu, username, message_chat, message_media, message_id, reply_to FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s'"%(bar[0][0],chat_id)
barR,jumR = eksekusi(sql_rangkum)

isi = []
for i in range(jumR):
    waktu = str( barR[i][0])
    username = str(barR[i][1])
    message_chat = str(barR[i][2])
    mc = message_chat.split(":")
    if mc[0]=='sticker':
        msg_chat = [[Image("logo.png", 2*inch, 2*inch)]]n
    else:
        msg_chat = message_chat
    print (msg_chat)

    message_media = str(barR[i][3])
    message_id = str(barR[i][4])
    reply_to = str(barR[i][5])

    dataisi ={
        'waktu':waktu, 
        'username':username,
        'msg_chat':msg_chat
        }
    isi.append(dataisi)


generate_commercial_invoice(header,isi,file_path = 'kulgram.pdf')
os.startfile('kulgram.pdf')