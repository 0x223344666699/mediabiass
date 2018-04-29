
# coding: utf-8

# ### TODOS
# #1 probar a comprobar todas las noticias vs. cada uno de los diccionarios

# In[1]:

import gensim
import pandas as pd
import logging
from IPython.core.display import display, HTML
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


# In[2]:

def clean_sentence(s):
    return gensim.parsing.stem_text(gensim.parsing.strip_multiple_whitespaces(gensim.parsing.strip_non_alphanum(gensim.parsing.strip_short(gensim.parsing.remove_stopwords(str(s).lower().replace("á", "a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")))))).split()


# In[4]:

news = pd.read_csv("df_news5.csv")

# procesado de noticias
periodicos = ["EM", "EP", "ABC"]
ls = {}
for p in periodicos:
    if p == "EM":
        linkweb = "http://www.elmundo.es"
    elif p == "EP":
        linkweb = "http://www.elpais.com"
    else:
        linkweb = "http://www.abc.es"
    titulares = list(news[news.periodico == linkweb].titular)
    noticias = list(news[news.periodico == linkweb].noticia)
    links = list(news[news.periodico == linkweb].link)
    ls[p] = {"titulares":titulares, "noticias":noticias, "links":links, "docs":[], "linkweb":linkweb}

# limpia de textos + creacion del diccionario
for p in periodicos:
    for s in ls[p]['noticias']: ls[p]['docs'].append(clean_sentence(s))
    ls[p]['dic'] = gensim.corpora.Dictionary(ls[p]['docs'])

def build_todos(ls):
    noticias_todos = []
    for p in periodicos: noticias_todos += ls[p]['noticias']

    docs_todos = []
    for s in noticias_todos: docs_todos.append(clean_sentence(s))
    dic_todos = gensim.corpora.Dictionary(docs_todos)
    dic_todos.filter_n_most_frequent(10)
    corpus = [dic_todos.doc2bow(doc) for doc in docs_todos]
    gensim.corpora.MmCorpus.serialize("./corpus.mm", corpus)
    return dic_todos

dic_todos = build_todos(ls)
corpus_todos = gensim.corpora.MmCorpus("./corpus.mm")

base = "ABC"
base2 = "EP"
comp = "EM"

dic_to_use = dic_todos #dic_wiki
corpus_to_use = corpus_todos #corpus_wiki

corpusbase = [dic_to_use.doc2bow(doc) for doc in ls[base]['docs']]
gensim.corpora.MmCorpus.serialize("./corpusbase.mm", corpusbase)

corpusbase2 = [dic_to_use.doc2bow(doc) for doc in ls[base2]['docs']]
gensim.corpora.MmCorpus.serialize("./corpusbase2.mm", corpusbase2)

corpusbase = gensim.corpora.MmCorpus("./corpusbase.mm")
corpusbase2 = gensim.corpora.MmCorpus("./corpusbase2.mm")


# In[7]:

# build models
tfidf = gensim.models.TfidfModel(corpus_to_use)
lsi = gensim.models.LsiModel(tfidf[corpus_to_use], id2word=dic_to_use, num_topics=20)
index = gensim.similarities.MatrixSimilarity(lsi[corpusbase], num_features=100) # transform corpus to LSI space and index it
index2 = gensim.similarities.MatrixSimilarity(lsi[corpusbase2], num_features=100) # transform corpus to LSI space and index it


# In[8]:

## print resultados
i = 0
for d in ls[comp]['docs']:
    vec_bow = dic_to_use.doc2bow(d)
    vec_lsi = lsi[tfidf[vec_bow]]
    sims = index[vec_lsi]
    sims = list(enumerate(sims))
    sims = sorted(sims, key=lambda t: -t[1])

    sims2 = index2[tfidf[vec_lsi]]
    sims2 = list(enumerate(sims2))
    sims2 = sorted(sims2, key=lambda t: -t[1])

    vec_bow = dic_to_use.doc2bow(ls[base]['docs'][sims[0][0]])
    vec_lsi = lsi[tfidf[vec_bow]]
    sims3 = index2[vec_lsi]
    sims3 = list(enumerate(sims3))
    sims3 = sorted(sims3, key=lambda t: -t[1])

    #if(sims[0][1] > 0.9) or (sims2[0][1] > 0.88) or (sims3[0][1] > 0.88):
    print("---------- " + comp + " vs. " + base + ": " + str(sims[0][1])+" ----------" + comp + " vs. " + base2 + ": " + str(sims2[0][1]) + " ------------ " + base + " vs. " + base2 + ": " + str(sims3[0][1]))
    display(HTML(str(i+1)+". "+comp+": " + ls[comp]['titulares'][i]+ ": <a href='" + ls[comp]['links'][i]+"'>Link</a>"))
    if(sims[0][1] > 0.93): display(HTML(str(i+1)+". "+base+": "+ls[base]['titulares'][sims[0][0]]+ ": <a href='"+ls[base]['links'][sims[0][0]]+"'>Link</a>"))
    if(sims2[0][1] > 0.88 and sims3[0][1] > 0.88) or sims2[0][1] > 0.93 or sims3[0][1] > 0.93: display(HTML(str(i+1)+". "+base2+": "+ls[base2]['titulares'][sims2[0][0]]+ ": <a href='"+ls[base2]['links'][sims2[0][0]]+"'>Link</a>"))

    i += 1


# In[ ]:




# In[ ]:
