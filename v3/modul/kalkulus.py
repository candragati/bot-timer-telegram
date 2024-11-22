
# from config import *
import threading
from mathpix.mathpix import MathPix
from sympy.parsing.latex import parse_latex
import wolframalpha
import pprint
# pip3 install antlr4-python3-runtime==4.7.1

# API_ID="uzairmahmed_gmail_com"
# API_KEY="59d1d27c256ef2b2a8ea"


APP_ID_W = "Q2HXJ5-GYYYX6PYYP"

# print (solve(expr))

API_ID="jcarroll"
API_KEY="13f1584b2f9edb8220bf619c0b4e3d5a"

lock = threading.Lock()

def itungin(update,context):
    bot = context.bot
    mathpix = MathPix(app_id=API_ID, app_key=API_KEY)     
    message = update.effective_message.reply_to_message    
    client = wolframalpha.Client(APP_ID_W)
    # detect media
    photo       = message.photo               
    if len(photo) != 0:            
        media       = photo[-1].file_id
        media_file  = bot.get_file(media)
        media_file.download('gambar/%s'%media)
        try:
            ocr = mathpix.process_image(image_path='gambar/%s'%media)
            expr1 = parse_latex(ocr.latex)
            expr2 = client.query(expr1)
            res1 = (expr2['pod'][0]['subpod']['plaintext'])
            update.message.reply_text(res1)
            res = client.query(res1)            
            pprint.pprint(res)        
            update.message.reply_text(next(res.results).text)
        except Exception as e:
            update.message.reply_text("males ah...%s"%e)
    else:
        update.message.reply_text("cuma bisa baca gambar")
        return


        

            


