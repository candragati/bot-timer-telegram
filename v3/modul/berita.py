
from config import *
import requests

kategori_en = ["business","entertainment","general","health","science","sports","technology"]
kategori_id = ["bisnis","hiburan","umum","kesehatan","sains","olahraga","teknologi"]

def berita(update,context):    
    b =  context.args
    if len(b) == 0:
        jenis = "top-headlines?country=id&"
    else:
        if b[0].lower()=='top':
            jenis =  "top-headlines?country=id&"
        elif b[0].lower()=='semua':
            jenis = "everything?"
        else:
            jenis = "top-headlines?country=id&"

    try:
        idx_cat = b.index('kategori')
        nama_cat =b[idx_cat+1]    
        cat = "category=%s&"%kategori_en[kategori_id.index(nama_cat)]
    except:
        cat = ""

    try:
        idx_key = b.index('keyword')
        key ="q=%s&"%b[idx_key+1]
    except:
        key = ""

    url = ("https://newsapi.org/v2/%s%s%sapiKey=%s"%(jenis,cat,key,Config.APINEWS))    
    data_teknologi = requests.get(url)
    status = data_teknologi.json()['status']
    if status == "ok":
        jum = data_teknologi.json()['totalResults']
        if jum==0:
            update.message.reply_markdown("Gak ada berita yang ditemukan")
        else:        
            if jum > 5:
                jum = 5        
            tampil =''.join('%s - [%s](%s)\n'%(str(i+1),data_teknologi.json()['articles'][i]['title'],data_teknologi.json()['articles'][i]['url']) for i in range(jum))            
            update.message.reply_markdown(tampil)
    else:
        update.message.reply_markdown('Error\n%s'%data_teknologi.json()['code'])

    '''
    https://newsapi.org/v2/everything?q=bitcoin&from=2019-04-14&sortBy=publishedAt&apiKey=API_KEY
    https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=API_KEY
    https://newsapi.org/v2/everything?q=apple&from=2019-05-13&to=2019-05-13&sortBy=popularity&apiKey=API_KEY
    https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=API_KEY
    https://newsapi.org/v2/everything?domains=wsj.com&apiKey=API_KEY
    '''

