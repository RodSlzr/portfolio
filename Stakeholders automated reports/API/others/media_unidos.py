#!/usr/bin/env python
# coding: utf-8

# In[1]:


#from newsapi import NewsApiClient
#import os
#import requests
#import spacy
#from os import listdir 
#import re
#import pandas as pd
#import numpy as np


# In[2]:


# Init
#newsapi = NewsApiClient(api_key='066cfe71329748e491e91b842a52ef6b')
# sources='the-hill,the-washington-post,associated-press,cbs-news,cnn,politico,the-washington-times,google-news,reuters',


# In[9]:
    
import os

os.chdir('/Users/javiergutierrez/app')
    

def run_all(i): 
    
    from newsapi import NewsApiClient
    newsapi = NewsApiClient(api_key='066cfe71329748e491e91b842a52ef6b')
    import os
    path = os.getcwd()
    a = select_query(i)
   # b = augment(a)
    c = json_normalize(a)
    d = set_keywords(c)
    e = only_keywords(d)
    f = to_csv(e)
    
    return e


def select_query(i):
    
    from newsapi import NewsApiClient
    newsapi = NewsApiClient(api_key='066cfe71329748e491e91b842a52ef6b')
    all_articles = newsapi.get_everything(q=i, 
                                      sources='the-hill,the-washington-post,associated-press,cbs-news,cnn,politico,the-washington-times,google-news,reuters',
                                      language='en')
    articles = all_articles['articles']
    b = dict_to_df(articles)
    return b

def dict_to_df(dictionary):
    
    import pandas as pd
    df1 = pd.DataFrame.from_dict(dictionary)
    return df1

def json_normalize(df):
    
    import pandas as pd
    df1 = pd.json_normalize(df['source'])
    df2 = df1.join(df)
    df3 = df2.drop(['urlToImage','source','name'], axis=1)
    df4 = df3.dropna()
    return df4


def set_keywords(df):
    
    import string
    import datetime as dt
    import pandas as pd
    from textblob import TextBlob

    keywords = ['mexico','usmca','trade', 'china', 'canada', 'trade agreement', 'tomatoe', 'sugar','tariff', 'american-made', 'auto',
           'katherine tai','guzman','dumping','antidumping', 'uyghur', 'commerce', 'raimondo',
           'foreign', 'vilsack','walsh','granholm', 'doc', 'nec', 'usda', 'doe', 'dol', 'dot', 'tai', 'trade agreement'
           'small business administration', 'itc', 'wto', 'sugar cane', 'semiconductor', 'supply chains', 'offshoring',
           'nearshoring', 'batteries', 'cool', 'chips', 'shortage', 'rubber', 'retaliation', 'steel', 'berries', 'solar panel',
           'automotive', 'manufacture', 'rules of origin', 'origin', 'section 232', 'section 301', 'section 201', 'section 332', 
           'substantial transformation', 'build back better', 'buy america', 'infrastructure bill', 'infrastructure plan',
           'incentives', 'pharmaceutical', 'advanced pharmaceutical ingredients', 'api','medical devices', 'medical equipment', 
            'personal protection equipment','ppe','back end', 'front end', 'usica', 'turtle excluded device', 'fertilizers',
           'grain oriented steel', 'unregulated fishing', 'roundup', "gmo's", 'potatoe','cotton', 'labeling', 
            'nom','competitiveness','strengthening america', 'competitive business','oce', 'bea','imports','exports',
            'local', 'protect national', 'protect american', 'domestic', 'domestic manufacturing','domestic production','picte',
            'market','regulator', 'regulations', 'clouthier','ebrard',\
            'Mexico', 'trade', 'commerce','imports', 'exports', 'tariffs', 'USMCA', 'subsidies','competition',\
            'automobile', 'vehicles', 'competitiveness', 'American jobs', 'mineral fuels', 'machinery',\
            'Trade','manufactures', 'maquiladoras', 'maquila', 'agriculture', 'tomato', 'soybeans', 'corn', \
            'pork', 'beef', 'Foreign Direct Investment', 'NAFTA', 'import tax', 'global trade',\
            'China', 'Canada', 'Trade Agreement', 'International Trade Commission', 'World Trade Organization',\
            'supply chains', 'offshoring', 'nearshoring', 'country of origin', 'sugar', 'dumping', \
            'retaliation', 'rules of origin', 'Section 232', 'Section 301', 'Section 201', 'Section 332',\
            'Buy America', 'vaquita marina', 'Vaquita Marina', 'Advanced Pharmaceutical Ingredients',\
            'Department of Commerce', 'Department of Agriculture', 'Department of Energy', 'COOL',\
            'Country of Origin Labeling', 'electric vehicles', 'budget reconciliation']
    s = set(keywords)
    df['text'] = df['title'] + ' ' + df['description'] + ' ' + df['content'] 
    df['text'] = df['text'].str.lower()
    df['keywords'] = [', '.join(set([y for y in x.split() if y in s])) for x in df['text']]
    df['sentiment'] = df['text'].apply(lambda summary:TextBlob(summary).sentiment.polarity)
    df['publishedAt'] = pd.to_datetime(df['publishedAt']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    #Contar cuantas palabras clave hay en el texto, resaltar aquellas que tienen mas de manera gradual 
    keys = df['keywords'].str.lower().str.split()
    df['num_key'] = keys.apply(len)
    df = df.sort_values(by=['publishedAt'], ascending=False)
    df = df.drop_duplicates()
    return df

def only_keywords(df): 
    
    import numpy as np
    # remplazar los espacios en blanco con NaN unicamente en la columna de 'keywords', quitar filas en las que hay NaN
    df['keywords'].replace('', np.nan, inplace=True)
    df.dropna(subset=['keywords'], inplace=True)
    df2 = df.drop(['text'], axis=1)
    # reorganizar columnas para ver informacion relevante primero
    df2 = df2[['id', 'title', 'publishedAt', 'keywords', 'num_key','description', 'content', 'sentiment','author', 'url']]
    return df2 
    

def to_csv(df):
    
    csv = df.to_csv('media1.csv', index=False)
    return csv  

#run_all(i)


# In[ ]:




