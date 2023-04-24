#!/usr/bin/env python
# coding: utf-8

# In[1]:
import os

os.chdir('/Users/javiergutierrez/app')


def run_all():
    
    
    # crear el PATH e incluir la clave para el API Key de comercio
    path = os.getcwd()
    headers = {'X-API-Key': '92uhWnPeyn8NW0Uh4wNhSXucTb7TUQSwCau0QBcm'}
    a = get_commerce()
    b = get_data(a)
    c = normalize_columns(b)
    d = augment(a, c)
    e = set_keywords(d)
    f = only_keywords(e)
    g = to_csv(f)
    
    return f

def get_commerce():

    import requests
    import re
    from urllib.request import urlopen, Request
    # funcion para pedir acceso al API y que regrese informacion en formato json 
    url='https://api.commerce.gov/api/news?api_key=92uhWnPeyn8NW0Uh4wNhSXucTb7TUQSwCau0QBcm'  
    r1 = requests.get(url)
    commerce = r1.json()
    return commerce

def get_data(commerce): 
    # seleccionar unicamente los datos del diccionario de json para crear la tabla
    data = commerce["data"]
    return data

def normalize_columns(data): 
    
    import pandas as pd
    import numpy as np
    # "aplanar" diccionarios que se encuentran dentro de otros diccionarios para utilizar los datos (record path)
    # mantener la variable 'uuid', el id especifico de cada noticia, (meta)
    # agregar un prefijo para reconocer que variable pertenece a cada diccionario (record_prefix)
    news = pd.json_normalize(
        data, 
        record_path =['news_type'],
        meta =['uuid'],
        record_prefix='news-')
    orgs = pd.json_normalize(
        data, 
        record_path =['orgs'],
        meta =['uuid'],
        record_prefix='orgs-')
    cat = pd.json_normalize(
        data, 
        record_path =['categories'],
        meta =['uuid'],
        record_prefix='category-')
    admin = pd.json_normalize(
        data, 
        record_path =['admin_officials'],
        meta =['uuid'],
        record_prefix='admin-')
    doc = pd.json_normalize(
        data, 
        record_path =['documents'],
        meta =['uuid'],
        record_prefix='doc-')
    tags = pd.json_normalize(
        data, 
        record_path =['tags'],
        meta =['uuid'],
        record_prefix='tags-')
    # utilizar merge (how = outer) para unir todas las tablas sobre la variable 'uuid' y tener una unica tabla
    df = news.merge(orgs, how='outer', on='uuid')
    df1 = df.merge(cat, how='outer', on='uuid')
    df2 = df1.merge(admin, how='outer', on='uuid')
    df3 = df2.merge(doc, how='outer', on='uuid')
    df4 = df3.merge(tags, how ='outer', on='uuid')
    # quitar variables que no son utiles usando drop
    df4 = df4.drop(['news-id','news-href','orgs-id','orgs-href','category-id','category-href',
                    'doc-id','doc-created','doc-filemime','doc-filesize', 'tags-id', 
                    'admin-id', 'tags-href', 'admin-href','doc-title'], axis=1)
    
    
    #df = [news, orgs, cat, admin, doc, tags]# categories	admin_officials	documents	tags	
    return df4

def augment(commerce, df):
    
    import pandas as pd
    import datetime
    #  convertir el diccionario completo en un "dataframe"
    df1 = pd.DataFrame.from_dict(commerce["data"])
    #funcion para unir dataframe original con el dataframe creado por funcion normalize_columns()
    df_final = df1.merge(df, how='outer', on='uuid')
    # quitar columnas que no se van a utilizar
    df_final = df_final.drop(['self','nid','publication','image','video',
                             'speaker','related','audience','galleries','teaser', 'news_type', 'tags',
                             'post_date', 'post_date_formatted','orgs','categories','admin_officials','subtitle',
                                    'documents', 'release_status'], axis=1)
    # cambiar las fechas de UNIX a date time (Y-m-d)
    df_final.created = df_final.created.apply(lambda d: datetime.datetime.fromtimestamp(int(d)).strftime('%Y-%m-%d'))
    df_final.updated = df_final.updated.apply(lambda d: datetime.datetime.fromtimestamp(int(d)).strftime('%Y-%m-%d'))
    # cambiar NaN por blank space, ordenar por fecha de lo mas reciente 
    df_final = df_final.fillna("")
    df_final = df_final.sort_values(by=['updated'], ascending=False)
    
    return df_final

#commerce = augment(commerce, df)
#commerce

def to_csv(df):
    
    csv = df.to_csv('commerce.csv', index=False)
    return csv

# lista de palabras clave que se van a utilizar

def set_keywords(df):
    
    import string
    from textblob import TextBlob
    
    keywords = ['mexico','usmca','trade', 'china', 'canada', 'trade agreement', 'tomatoe', 'sugar','tariff', 'american-made', 'auto',
           'katherine tai','guzman','dumping','antidumping', 'uyghur', 'commerce', 'raimondo', 'tai',
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
            'market','regulator', 'regulations']
    s = set(keywords)
    df['body'].str.lower()
    df['keywords'] = [', '.join(set([y for y in x.split() if y in s])) for x in df['body']]
    df['sentiment'] = df['body'].apply(lambda summary:TextBlob(summary).sentiment.polarity)
    
    # reorganizar columnas para ver informacion relevante primero
    df = df[['label','news-label', 'created', 'updated','keywords','orgs-label','category-label',
          'admin-label','tags-label','sentiment','href','doc-href','body','uuid','id']]
    return df

def only_keywords(df): 
    
    import numpy as np
    # remplazar los espacios en blanco con NaN unicamente en la columna de 'keywords', quitar filas en las que hay NaN
    df['keywords'].replace('', np.nan, inplace=True)
    df.dropna(subset=['keywords'], inplace=True)
    df2 = df.drop(['body', 'uuid'], axis=1)
    return df2 

#run_all()


# In[2]:


#df_final = only_keywords(df)
#df_final.to_csv(r'/Users/paulagaviria/myproject/commerce_news.csv', index=False)


# In[3]:


#import dtale
#d = dtale.show(df_final)
#d.open_browser()


# In[ ]:




