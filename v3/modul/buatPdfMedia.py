from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Preformatted, PageBreak
from reportlab.lib.units import cm,mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors, utils
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from config import *
from datetime import *
import html
from bidi.algorithm import get_display
from arabic_reshaper import ArabicReshaper
# from emojipy import Emoji
import emoji
from emojipy import Emoji
import re


Emoji.unicode_alt = False


def replace_with_emoji_pdf(text, size):
    """
    Reportlab's Paragraph doesn't accept normal html <image> tag's attributes
    like 'class', 'alt'. Its a little hack to remove those attrbs
    """

    text = Emoji.to_image(text)
    text = text.replace('class="emojione"', 'height=%s width=%s' %(size, size))
    return re.sub('alt="'+Emoji.shortcode_regexp+'"', '', text)

configuration = {
    'delete_harakat': False,
    'support_ligatures': False,    
}
reshaper = ArabicReshaper(configuration=configuration)

class PageNumCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        page_count = len(self.pages)       
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)            
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page = "Page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(195*mm, 10*mm, page)

def buatPdf(chat_id):
    width, height = A4
    namafile    = "media%s.pdf"%(abs(chat_id))
    pdfmetrics.registerFont(TTFont('Candara','arial_0.ttf'))
    pdfmetrics.registerFont(TTFont('CandaraBold','arialbd_0.ttf'))
    pdfmetrics.registerFont(TTFont('CandaraItalic','ariali_0.ttf'))

    doc = SimpleDocTemplate(namafile, rightMargin=.5 * cm, leftMargin=.5 * cm,topMargin=.5 * cm, bottomMargin=1.5 * cm)
    story = []        
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Line_Data', fontName='Candara',alignment=TA_LEFT, fontSize=10, leading=10))
    # styles.add(ParagraphStyle(name='Line_Data_Angka', fontName='Candara',alignment=TA_RIGHT, fontSize=8, leading=7))
    # styles.add(ParagraphStyle(name='Line_Data_Small', fontName='Candara',alignment=TA_LEFT, fontSize=7, leading=8))
    styles.add(ParagraphStyle(name='Line_Data_Large', fontName='CandaraBold',alignment=TA_LEFT, fontSize=11, leading=12))
    # styles.add(ParagraphStyle(name='Line_Data_Largest', fontName='Candara',alignment=TA_LEFT, fontSize=15, leading=15))
    styles.add(ParagraphStyle(name='Line_Label', fontName='Candara', fontSize=11, leading=13, alignment=TA_LEFT, wordWrap = True))
    # styles.add(ParagraphStyle(name='Line_Label_Center', fontName='Candara', fontSize=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='judul', fontName='CandaraBold', fontSize=16, alignment=TA_CENTER,leading = 20))
    styles.add(ParagraphStyle(name='username', fontName='CandaraBold', fontSize=11, alignment=TA_LEFT,leading = 7))
    styles.add(ParagraphStyle(name='reply', fontName='CandaraItalic', fontSize=10, alignment=TA_LEFT,leading = 10))    

    data1 = [
        [Paragraph('Export media', styles["Line_Data_Large"]),
         Paragraph('', styles["Line_Data_Large"]),
         Paragraph('', styles["Line_Data_Large"])
        ],
        [Paragraph('', styles["Line_Data_Large"]),
         Paragraph('', styles["Line_Data_Large"]),         
         Paragraph('', styles["Line_Data_Large"])]]

    t1 = Table(data1, colWidths=('70%','10%','20%'))
    t1.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (0, 1), 0.25, colors.black),    
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),    
    ]))
    story.append(t1)
    story.append(Spacer(0.1 * cm, .5 * cm))
    
    sql = "SELECT nomor,waktu, media_tipe, media_keyword,thumb_id, image_size  FROM media WHERE chat_id = '%s'"%chat_id
    barR, jumR = eksekusi(sql)
    
    for i in range(jumR):        
        nomor       = barR[i][0]
        waktu       = barR[i][1]
        # waktu       = datetime.strptime(waktu,"%Y-%m-%d %H:%M:%S")
        m_tipe      = barR[i][2]
        m_keyword   = barR[i][3]
        m_id        = barR[i][4]
        
        try:
          width,height = (int(b) for b in barR[i][5].split("x"))
        except Exception as a:          
          width,height = [0,0]
        

        if width > 200:
          aspect  = height / float(width)
          width   = 100
          height  = (width * aspect)
        else:
          pass
        

        mc = str(m_id)

        if width ==0 and height == 0:            
            pict = Paragraph("preview tidak tersedia", styles["Line_Label"])
        else:
            pict = Image("gambar/%s"%mc,width = width,height = height)
        # waktu = Paragraph(waktu, styles["Line_Label"])
        # tipe = Paragraph(m_tipe, styles["Line_Label"])
        keyword = Paragraph(m_keyword, styles["Line_Label"])
        caption = "%s\n%s\n%s "%(m_tipe, m_keyword,waktu)
        caption = Preformatted(caption, styles["Line_Label"],maxLineLength = 96)
          
        dataLISTwidth = ('25%','10%',None,'1%')
        
        data1 = [
          [caption,pict,'',''],          
        ]
        t1 = Table(data1, colWidths=dataLISTwidth)
        t1.setStyle(TableStyle([
          # ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
          # ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),     
          # ('SPAN',(1,0),(2,0)),   
          # ('SPAN',(1,1),(2,1)),   
        ]))
        t1.hAlign = 'LEFT'
        story.append(t1)        
        story.append(Spacer(0.1 * cm, 1 * cm))       

    doc.build(story,canvasmaker = PageNumCanvas)


# buatPdf(-1001286308688)