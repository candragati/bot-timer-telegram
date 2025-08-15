
from config import *
import feedparser

def berita(update,context):    
    b =  context.args
    url = "https://news.google.com/rss"
    bahasa = ""
    key = ""
    if len(b) == 0:
        bahasa = ""
    elif len(b) == 1:
        if b[0].lower()=='id':
            bahasa =  "?hl=id&gl=ID&ceid=ID:id"  
        elif b[0].lower() == 'en':
            bahasa = "?hl=en-ID&gl=ID&ceid=ID:en"
        else:
            update.message.reply_markdown("gunakan hanya 'id' dan 'en' saja.")      
            return
    else:
        if b[0].lower()=='id':
            bahasa =  "&hl=id&gl=ID&ceid=ID:id"        
        elif b[0].lower() == 'en':
            bahasa = "&hl=en-ID&gl=ID&ceid=ID:en"
        else:
            updatem.message.reply_markdown("gunakan hanya 'id' dan 'en' saja.")      
            return
        key = "/search?q="+"+".join(b[1:])
    
    url = f"{url}{key}{bahasa}"    
    feed = feedparser.parse(url)
    isiBerita = []
    for i,entry in enumerate(feed.entries[:10]):
        link = entry.link
        title = entry.title
        isiBerita.append(f"{i+1}. [{title}]({link})\n")
    tampil = ''.join(isiBerita)
    update.message.reply_markdown(tampil)

    