# ### TODOS
# 1. 
# 2. 

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
PATH = './'
news = pd.read_csv(PATH + 'df_news_feed.csv')


# procesado de noticias
periodicos = ["elmundo", "elpais"]
ls = {}
for periodico in periodicos:
    titulares = list(news[news.newspaper == periodico].titular)
    noticias = list(news[news.newspaper == periodico].noticia)
    links = list(news[news.newspaper == periodico].link)
    ls[periodico] = {"titulares":titulares, "noticias":noticias, "links":links, "docs":[], "periodico":periodico}

# limpia de textos + creacion del diccionario
for periodico in periodicos:
    noticias = ls[periodico]['noticias']
    for noticia in noticias:
         ls[periodico]['docs'].append(clean_sentence(noticia))
    ls[periodico]['dic'] = gensim.corpora.Dictionary(list(ls[periodico]['docs']))
# In[]:
def build_todos_dic(ls):
    noticias_todos = []
    for periodico in periodicos: 
        noticias_todos += ls[periodico]['noticias']

    docs_todos = []
    for noticia in noticias_todos: 
        docs_todos.append(clean_sentence(noticia))

    dic_todos = gensim.corpora.Dictionary(docs_todos)
    dic_todos.filter_n_most_frequent(10)
    corpus = [dic_todos.doc2bow(doc) for doc in docs_todos]
    gensim.corpora.MmCorpus.serialize(PATH + "corpus.mm", corpus)
    return dic_todos
# In[]:

dic_todos = build_todos_dic(ls)
corpus_todos = gensim.corpora.MmCorpus(PATH + "corpus.mm")

base = "elpais"
comp = "elmundo"

dic_to_use = dic_todos #dic_wiki
corpus_to_use = corpus_todos #corpus_wiki

corpusbase = [dic_to_use.doc2bow(doc) for doc in ls[base]['docs']]
gensim.corpora.MmCorpus.serialize(PATH + "corpusbase.mm", corpusbase)

corpusbase = gensim.corpora.MmCorpus(PATH + "corpusbase.mm")


# In[7]:

# build models
tfidf = gensim.models.TfidfModel(corpus_to_use)
lsi = gensim.models.LsiModel(tfidf[corpus_to_use], id2word=dic_to_use, num_topics=10)
index = gensim.similarities.MatrixSimilarity(lsi[corpusbase], num_features=100) # transform corpus to LSI space and index it


# In[8]:

## print resultados
i = 0
for d in ls[comp]['docs']:
    vec_bow = dic_to_use.doc2bow(d)
    vec_lsi = lsi[tfidf[vec_bow]]
    sims = index[vec_lsi]
    sims = list(enumerate(sims))
    sims = sorted(sims, key=lambda t: -t[1])

    vec_bow = dic_to_use.doc2bow(ls[base]['docs'][sims[0][0]])
    vec_lsi = lsi[tfidf[vec_bow]]

    display("---------- " + comp + " vs. " + base + ": " + str(sims[0][1])+" ----------")
    display(HTML(str(i+1)+". "+comp+": " + ls[comp]['titulares'][i]+ ": <a href='" + ls[comp]['links'][i]+"'>Link</a>"))
    if(sims[0][1] > 0.9): display(HTML(str(i+1)+". "+base+": "+ls[base]['titulares'][sims[0][0]]+ ": <a href='"+ls[base]['links'][sims[0][0]]+"'>Link</a>"))

    i += 1
