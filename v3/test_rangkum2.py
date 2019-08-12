# -*- coding: utf_8 -*-
from config import *

import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import inch,cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Candara','Candara.ttf'))
pdfmetrics.registerFont(TTFont('CandaraBold','Candarab.ttf'))

chat_id  = '-1001337729941'
sql = "SELECT nomor,waktu, judul, author,chat_title  FROM rekam WHERE chat_id = '%s' AND done = 0"%chat_id
bar, jum = eksekusi(sql)
nomor =  bar[0][0]
waktu =  bar[0][1]
judul =  bar[0][2]
author =  bar[0][3]
chat_title =  bar[0][4]
tanggalexp=datetime.strptime(waktu,"%Y-%m-%d")
waktu=tanggalexp.strftime("%d %b %Y")
namafile = "%s%s.pdf"%(chat_title, nomor)

header = {
  'chat_id' : chat_id, 
  'chat_title' : chat_title, 
  'no'      : nomor,
  'judul'   : judul,
  'author'  : author,
  'waktu'   : waktu,
  }

    
    

doc = SimpleDocTemplate(namafile, rightMargin=.5 * cm, leftMargin=.5 * cm,topMargin=.5 * cm, bottomMargin=1.5 * cm)
story = []        
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
styles.add(ParagraphStyle(name='Line_Data', fontName='Candara',alignment=TA_LEFT, fontSize=8, leading=7))
styles.add(ParagraphStyle(name='Line_Data_Angka', fontName='Candara',alignment=TA_RIGHT, fontSize=8, leading=7))
styles.add(ParagraphStyle(name='Line_Data_Small', fontName='Candara',alignment=TA_LEFT, fontSize=7, leading=8))
styles.add(ParagraphStyle(name='Line_Data_Large', fontName='CandaraBold',alignment=TA_LEFT, fontSize=12, leading=12))
styles.add(ParagraphStyle(name='Line_Data_Largest', fontName='Candara',alignment=TA_LEFT, fontSize=14, leading=15))
styles.add(ParagraphStyle(name='Line_Label', fontName='Candara', fontSize=7, leading=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='Line_Label_Center', fontName='Candara', fontSize=7, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='judul', fontName='CandaraBold', fontSize=15, alignment=TA_CENTER,leading = 20))
styles.add(ParagraphStyle(name='username', fontName='CandaraBold', fontSize=7, alignment=TA_LEFT,leading = 7))

data1 = [
    [Paragraph('<b>%s</b>'%(header['chat_title']), styles["Line_Data_Large"]), '',
     Paragraph('Tanggal', styles["Line_Data_Large"]),
     Paragraph(':', styles["Line_Data_Large"]),
     Paragraph(header['waktu'], styles["Line_Data_Large"])
    ],
    [Paragraph('kulgram ke %s'%header['no'], styles["Line_Data_Large"]), '',
     Paragraph('Author', styles["Line_Data_Large"]),
     Paragraph(':', styles["Line_Data_Large"]),
     Paragraph('@%s'%header['author'], styles["Line_Data_Large"])]]

t1 = Table(data1, colWidths=(8*cm, 4.3*cm, 2.5*cm,0.3*cm,None))
t1.setStyle(TableStyle([
    ('INNERGRID', (0, 0), (0, 1), 0.25, colors.black),
]))
story.append(t1)


story.append(Spacer(0.1 * cm, .5 * cm))
story.append(Paragraph("<b>%s</b>"%header['judul'], styles["judul"]))
story.append(Spacer(0.1 * cm, .1 * cm))

sql_rangkum = "SELECT waktu, nama, message_chat, message_media, message_id, reply_to,username FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s'"%(bar[0][0],chat_id)
barR,jumR = eksekusi(sql_rangkum)

isi = []
for i in range(jumR):
    waktu = str( barR[i][0])
    username = str( barR[i][6])
    nama = barR[i][1].encode('utf-8')
    tanggalexp=datetime.strptime(waktu,"%Y-%m-%d %H:%M:%S")
    waktu=tanggalexp.strftime("%H:%M:%S")
    dataLISTwidth = ('8%','8%','84%')
    
    # gambar = Image("Candragati",width = 32, height = 32)
    data1 = [[Paragraph('<img src = "media/%s" width = 32 height = 32 valign = "top"></img>'%username, styles["Line_Data"]),
              Paragraph('<font size = 8 color = grey>%s</font>'%waktu, styles["Line_Data"]),
              Paragraph(nama, styles["username"]),
              ]]
        
    t1 = Table(data1, colWidths=dataLISTwidth)            
    t1.hAlign = 'LEFT'
    t1.setStyle(TableStyle([
        # ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        # ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),

    ]))
    story.append(t1)
    
    message_chat = str(barR[i][2])
    mc = message_chat.split(":")
    # print mc
    if mc[0]=='sticker':
      m_chat = Image(mc[1],width = 64, height = 64)      
    else:   
      m_chat = Paragraph(message_chat, styles["Line_Label"])
    
    data1 = [[
      Paragraph('', styles["Line_Label"]),
      m_chat,
      Paragraph('', styles["Line_Label"]),
    ]]
    dataLISTwidth = ('8%','8%','84%')
    t1 = Table(data1, colWidths=dataLISTwidth)
    t1.setStyle(TableStyle([
      # ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
      # ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
      # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),     
      ('SPAN',(1,0),(2,0))   
    ]))
    t1.hAlign = 'LEFT'      

    message_media = str(barR[i][3])
    message_id = str(barR[i][4])
    reply_to = str(barR[i][5])
    story.append(t1)
    story.append(Spacer(0.1 * cm, .5 * cm))
doc.build(story)



# os.startfile(namafile)
