from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import *
from datetime import datetime
import html

def buatPdf(chat_id):    
    pdfmetrics.registerFont(TTFont('Candara','Candara.ttf'))
    pdfmetrics.registerFont(TTFont('CandaraBold','Candarab.ttf'))
    pdfmetrics.registerFont(TTFont('CandaraItalic','Candarai.ttf'))

    sql = "SELECT nomor,waktu, judul, author,chat_title  FROM rekam WHERE chat_id = '%s' AND done = 0"%chat_id
    bar, jum = eksekusi(sql)
    nomor       = bar[0][0]
    waktu       = bar[0][1]
    judul       = bar[0][2]
    author      = bar[0][3]
    chat_title  = bar[0][4]
    tanggalexp  = datetime.strptime(waktu,"%Y-%m-%d")
    waktu       = tanggalexp.strftime("%d %b %Y")
    namafile    = "%s%s.pdf"%(abs(chat_id), nomor)

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
    styles.add(ParagraphStyle(name='Line_Data', fontName='Candara',alignment=TA_LEFT, fontSize=10, leading=7))
    # styles.add(ParagraphStyle(name='Line_Data_Angka', fontName='Candara',alignment=TA_RIGHT, fontSize=8, leading=7))
    # styles.add(ParagraphStyle(name='Line_Data_Small', fontName='Candara',alignment=TA_LEFT, fontSize=7, leading=8))
    styles.add(ParagraphStyle(name='Line_Data_Large', fontName='CandaraBold',alignment=TA_LEFT, fontSize=11, leading=12))
    # styles.add(ParagraphStyle(name='Line_Data_Largest', fontName='Candara',alignment=TA_LEFT, fontSize=15, leading=15))
    styles.add(ParagraphStyle(name='Line_Label', fontName='Candara', fontSize=8, leading=9, alignment=TA_LEFT))
    # styles.add(ParagraphStyle(name='Line_Label_Center', fontName='Candara', fontSize=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='judul', fontName='CandaraBold', fontSize=16, alignment=TA_CENTER,leading = 20))
    styles.add(ParagraphStyle(name='username', fontName='CandaraBold', fontSize=10, alignment=TA_LEFT,leading = 7))
    styles.add(ParagraphStyle(name='reply', fontName='CandaraItalic', fontSize=10, alignment=TA_LEFT,leading = 7))

    data1 = [
        [Paragraph(header['chat_title'], styles["Line_Data_Large"]),
         Paragraph('Tanggal', styles["Line_Data_Large"]),
         Paragraph(header['waktu'], styles["Line_Data_Large"])
        ],
        [Paragraph('kulgram ke %s'%header['no'], styles["Line_Data_Large"]),
         Paragraph('Author', styles["Line_Data_Large"]),         
         Paragraph('@%s'%header['author'], styles["Line_Data_Large"])]]

    t1 = Table(data1, colWidths=('70%','10%','20%'))
    t1.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (0, 1), 0.25, colors.black),    
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),    
    ]))
    story.append(t1)
    story.append(Spacer(0.1 * cm, .5 * cm))
    story.append(Paragraph("<b>%s</b>"%header['judul'], styles["judul"]))
    story.append(Spacer(0.1 * cm, .1 * cm))

    sql_rangkum = "SELECT waktu, nama, message_chat, message_media, message_id, reply_to,username,forward_username, forward_name FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s'"%(bar[0][0],chat_id)
    barR,jumR = eksekusi(sql_rangkum)

    for i in range(jumR):
        waktu         = str( barR[i][0])
        username      = str(barR[i][6])
        nama          = barR[i][1]
        tanggalexp    = datetime.strptime(waktu,"%Y-%m-%d %H:%M:%S")
        waktu         = tanggalexp.strftime("%H:%M:%S")
        dataLISTwidth = ('8%','8%','84%')
        reply_to      = barR[i][5]
        forward_username = barR[i][7]
        

        if reply_to == '0':
          pass
        else:
          baca_reply = "SELECT waktu, nama, message_chat FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s' AND message_id = '%s'"%(bar[0][0],chat_id,reply_to)
          barReply,jumReply = eksekusi(baca_reply)

          if jumReply == 0:
            pass
          else:

            try:
              message_chat = barReply[0][2].decode('utf-8')
            except Exception as e:
              message_chat = barReply[0][2]
            waktureply = datetime.strptime(barReply[0][0],"%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            data1 = [[
              Paragraph('', styles["Line_Label"]),
              Paragraph('<font size = 8 color = grey>%s</font>'%waktureply, styles["reply"]),
              Paragraph('%s <font color= grey>%s</font>'%((barReply[0][1]),str(message_chat).replace("\\n","<br/>")), styles["reply"]),
            ]]
            dataLISTwidth = ('8%','8%','84%')
            t1 = Table(data1, colWidths=dataLISTwidth)            
            t1.hAlign = 'LEFT'
            t1.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            story.append(t1)   

        if forward_username is None:
          try:
            data1 = [[
                Paragraph('<img src = "gambar/%s" width = 32 height = 32 valign = "top"></img>'%username, styles["Line_Data"]),
                Paragraph('<font size = 8 color = grey>%s</font>'%waktu, styles["Line_Data"]),
                Paragraph(html.escape(nama), styles["username"]),
                ]]
          except:
            data1 = [[
                Paragraph('', styles["Line_Data"]),
                Paragraph('<font size = 8 color = grey>%s</font>'%waktu, styles["Line_Data"]),
                Paragraph(html.escape(nama), styles["username"]),
                ]]
        else:
          try:
            data1 = [[
                Paragraph('<img src = "gambar/%s" width = 32 height = 32 valign = "top"></img>'%username, styles["Line_Data"]),
                Paragraph('<font size = 8 color = grey>%s</font>'%waktu, styles["Line_Data"]),
                Paragraph("Forwarded from %s"%html.escape(forward_username), styles["username"]),
                ]]
          except:
            data1 = [[
                Paragraph('', styles["Line_Data"]),
                Paragraph('<font size = 8 color = grey>%s</font>'%waktu, styles["Line_Data"]),
                Paragraph("Forwarded from %s"%html.escape(forward_username), styles["username"]),
                ]]
        t1 = Table(data1, colWidths=dataLISTwidth)            
        t1.hAlign = 'LEFT'
        t1.setStyle(TableStyle([
            # ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t1)

        
        try:
          message_chat = barR[i][2].decode('utf-8')
        except:
          message_chat = barR[i][2]
        mc = str(barR[i][3])                
        
        if mc=='':
          pict = Paragraph('', styles["Line_Data"])
        else:
          pict = Image("gambar/%s"%mc,width = 128, height = 128)

        if message_chat == "":
          caption = Paragraph('', styles["Line_Data"])
        else:
          caption = Paragraph(str(message_chat).replace("<","&lt;").replace(">","&gt;").replace("\\n","<br/>"), styles["Line_Label"])
        
        data1 = [
          [Paragraph('', styles["Line_Label"]),pict,Paragraph('', styles["Line_Label"]),],
          [Paragraph('', styles["Line_Label"]),caption,Paragraph('', styles["Line_Label"])]
        ]
        dataLISTwidth = ('8%','8%','84%')
        t1 = Table(data1, colWidths=dataLISTwidth)
        t1.setStyle(TableStyle([
          # ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
          # ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
          # ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),     
          ('SPAN',(1,0),(2,0)),   
          ('SPAN',(1,1),(2,1)),   
        ]))
        t1.hAlign = 'LEFT'      

        story.append(t1)
        story.append(Spacer(0.1 * cm, .5 * cm))
    doc.build(story)

# buatPdf(-1001162202776) # koding Teh
# buatPdf(-1001337729941) # backup darurat
