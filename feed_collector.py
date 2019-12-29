import feedparser
import pandas as pd
from bs4 import BeautifulSoup
import requests
import unicodedata
import string

## http://rss.elmundo.es/rss/
## 

urls_dic = {
    'elpais': ['http://ep00.epimg.net/rss/politica/portada.xml', 'http://ep00.epimg.net/rss/ccaa/madrid.xml', 'http://ep00.epimg.net/rss/economia/portada.xml'],
    'elmundo': ['https://e00-elmundo.uecdn.es/elmundo/rss/espana.xml', 'https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml', 'https://e00-elmundo.uecdn.es/elmundo/rss/madrid.xml']
}

keywords_dic = {
    'elpais': ['politica', 'economia', 'sociedad'],
    'elmundo': ['espana', 'madrid', 'economia']
}
counter = {
    'elpais': 0,
    'elmundo': 0
}

def get_noticia(newspaper, link):
    print('Fetching ', entry.link, '\n')

    r = requests.get(link).text
    soup = BeautifulSoup(r, "html.parser")
    noticia = ''
    for p in soup.find_all('p'):
        n = p.text
        noticia += ' ' + n.replace('\n', ' ')

    print(clean_noticia(noticia))
    return clean_noticia(noticia)

def clean_noticia(noticia):
    noticia = clean_text_lower(noticia)
    # noticia = clean_text_punctuation(noticia)
    noticia = clean_text_accents(noticia)
    return noticia

def clean_text_accents(txt, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize('NFD', txt) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))

def clean_text_punctuation(txt):
    txt = txt.translate(str.maketrans('', '', string.punctuation))
    return txt

def clean_text_lower(txt):
    txt = txt.lower()
    return txt

dic_news = {'newspaper':[], "titular":[], "noticia":[], "link":[]}
for newspaper in urls_dic:
    print('------------ ', newspaper,' --------------')
    for suburl in urls_dic[newspaper]:
        newsfeed = feedparser.parse(suburl)
        for entry in newsfeed.entries:
            counter[newspaper] += 1
            # print('\t', entry.title, '\n\t\t', entry.link, '\n')
            dic_news['newspaper'].append(newspaper)
            dic_news['titular'].append(entry.title)
            dic_news['link'].append(entry.link)
            dic_news['noticia'].append(get_noticia(newspaper,entry.link))


print('Total: ',counter)
df_news = pd.DataFrame(dic_news)
df_news.to_csv('df_news_feed.csv', encoding="UTF-8", index=False)
