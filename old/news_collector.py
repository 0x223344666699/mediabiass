
# coding: utf-8

# In[1]:

from bs4 import BeautifulSoup
import requests
import pandas as pd
# In[]

# newspapers = ["http://www.elmundo.es", "http://www.elconfidencial.com", "http://www.abc.es", "http://www.elpais.com"]
newspapers = ["http://www.elmundo.es", "http://www.elpais.com"]
dic_news = {"periodico":[], "titular":[], "noticia":[], "link":[]}
categories_to_avoid = ["summum/estilo", "/verne", "/eventos", "/icon", "/cincodias", "/futbol", "/elcomidista", "/retina", "/tecnologia","/motor", "/loc/", "/television", "opinion", "deportes", "video", "galeria", "multimedia", "/loc/famosos", "/estilo/gente", "vanitatis", "cultura", "/play/", "metropoli", "ciencia-y-salud", "salud", "viajes", "plan-b", "/f5/", "/papel/", "/vida-sana/"]
old_df_news = pd.DataFrame(dic_news)

for np in newspapers:
    print("------ " + np + " -------")
    r = requests.get(np).text
    soup = BeautifulSoup(r, "html.parser")
    count = 0

    s = soup.find_all("h3", {"class":"mod-title"})
    if np == "http://www.elconfidencial.com":
        s = soup.find_all("h3", {"class":"art-tit"})
    if np == "http://www.abc.es":
        s = soup.find_all("h1", {"class":"titular"})
    if np == "http://www.elpais.com":
        s = soup.find_all("h2", {"class":"articulo-titulo"})

    for t in s:
        count += 1
        txt = t.text
        txt = txt.replace("\n", "")
        if (t.a is not None):
            #get link of article
            href = t.a['href']
            if (not any(cat in href for cat in categories_to_avoid)):
                if ("http://" not in href) and ("https://" not in href):
                    print("\t ADDING np: "+href)
                    href = np+href

                if href not in (old_df_news['link'].tolist()):
                    rn = requests.get(href).text
                    #parse article
                    soup_news = BeautifulSoup(rn, "html.parser")
                    ## elmundo.es
                    divn = soup_news.find("div", {"itemprop":  "articleBody"})
                    if np == "http://www.elconfidencial.com":
                        divn = soup_news.find("div", {"id":  "news-body-center"})
                    if np == "http://www.abc.es":
                        divn = soup_news.find("span", {"class":  "cuerpo-texto"})
                    if np == "http://www.pais.com":
                        divn = soup_news.find("div", {"itemprop":  "articleBody"})

                    if (divn is not None):
                        noticia = ""
                        for p in divn.find_all("p"):
                            n = p.text
                            if 'class' in p.attrs: print(n)
                            if "ELMUNDO" not in n and "Síguenos en" not in n and 'class' not in p.attrs: noticia += " "+n
                        if noticia != "":
                            dic_news["periodico"].append(np)
                            dic_news["titular"].append(txt)
                            dic_news["noticia"].append(noticia)
                            dic_news["link"].append(href)
                            print("AÑADIENDO: " + href)
                    else:
                        print("DIVN IS NONE: " + href)
                else:
                    print("YA PRESENTE: " + href)
            else:
                print("EVITADO: " + href)
    print(count)


# In[3]:

df_news = pd.DataFrame(dic_news)
print(old_df_news.shape)
new_df_news = old_df_news.append(df_news, ignore_index=True)
new_df_news.to_csv("df_news.csv", encoding="UTF-8", index=False)
print(new_df_news.shape)


# In[20]:

import re
new_df_news.noticia.apply(lambda x: print(re.findall("[a-zA-Z][a-zñ]*",str(x).replace("á", "a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u"))))


# In[52]:

new_df_news = pd.read_csv("df_news.csv")
print(new_df_news.shape)
new_df_news = new_df_news[new_df_news['link'].apply(lambda x: "/xxx" not in x)]
print(new_df_news.shape)


# In[51]:

new_df_news = new_df_news[["link", "noticia", "periodico", "titular"]]
new_df_news.to_csv("df_news.csv", encoding="UTF-8", index=False)


# In[ ]:
