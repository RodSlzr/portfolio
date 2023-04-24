#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 10:18:43 2021

@author: javiergutierrez
"""

## Library load

from flask import Flask, render_template, send_file, make_response, url_for, Response, request
import pandas as pd
import os
import requests
import spacy
from os import listdir 
import re
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from PyPDF2 import PdfFileWriter, PdfFileReader
from urllib.request import urlopen, Request
from congress import Congress
import scrapy 
from scrapy.selector import Selector
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob, Word, Blobber
from textblob.classifiers import NaiveBayesClassifier
from textblob.taggers import NLTKTagger
import urllib
import urllib3
from urllib.request import unquote
import PyPDF2

nlp = spacy.load("en_core_web_sm")


# In[29]:

## Definimos directorio, lista de comités para búsqueda y keywords.


os.chdir('/Users/javiergutierrez/app')

path = os.getcwd()

clase = ['Congress', 'Political Statements', 'News & Media']

committees = 	['House Foreign Affairs Committee', 'House Agriculture Committee', \
    'Senate Commerce, Science, and Transportation Committee', 'Senate Foreign Relations Committee',\
    'House Energy and Commerce Committee','House Agriculture Committee', 'House Ways and Means Committee',\
    'House Small Business Committee', 'House Natural Resources Committee',\
        'House Financial Services Committee','Senate Agriculture, Nutrition, and Forestry Committee',\
            'Senate Finance Committee', 'House Rules Committee', 'House Budget Committee']
    
keywords = ['Mexico', 'trade', 'commerce','imports', 'exports', 'tariffs', 'USMCA', 'subsidies','competition'\
            'automobile', 'vehicles', 'competitiveness', 'American jobs', 'mineral fuels', 'machinery',\
            'Trade','manufactures', 'maquiladoras', 'maquila', 'agriculture', 'tomatoes', 'soybeans', 'corn', \
            'pork', 'beef', 'Foreign Direct Investment', 'NAFTA', 'import tax', 'global trade',\
            'China', 'Canada', 'Trade Agreement', 'International Trade Commission', 'World Trade Organization',\
            'supply chains', 'offshoring', 'nearshoring', 'country of origin', 'sugar', 'dumping', \
            'retaliation', 'rules of origin', 'Section 232', 'Section 301', 'Section 201', 'Section 332',\
            'Buy America', 'vaquita marina', 'Vaquita Marina', 'Advanced Pharmaceutical Ingredients',\
            'Department of Commerce', 'Department of Agriculture', 'Department of Energy', 'COOL',\
                'Country of Origin Labeling', 'electric vehicles', 'budget reconciliation', 'global trade'] 


# Función para definir url de búsqueda

def url_fun(tipo,i):
        if tipo == 'Congress':
            url = 'https://api.propublica.org/congress/v1/bills/search.json?query='+ i    
            
        elif tipo == 'Political Statements':
            url = 'https://api.propublica.org/congress/v1/statements/search.json?query='+ i
            
        else:
            url = 'pendiente'
            
        return(url)
            


# In[31]:


# Funciones para obtener info de url por tipo de búsqueda

headers = {'X-API-Key': 'Qoc26kX4ASSpatIYaMhAAtk4RFYlO24gb2Z8VZZW'}
    
def members_fun(tipo, i):
    url = url_fun(tipo,i)
    r1 = requests.get(url, headers=headers)
    memberdata = r1.json()
    return(memberdata)


def statement_fun(tipo, i):
    try:
        if tipo == 'Political Statements':
            statements_df = pd.DataFrame() 
            memberdata= members_fun(tipo, i)
            for f in range(len(memberdata["results"])):
                info_statement = pd.DataFrame.from_dict(memberdata["results"][f], orient = 'index')
                info_statement = info_statement.transpose()
                statements_df = statements_df.append(info_statement) 
                statements_df = statements_df.reset_index(drop = True) 
            return(statements_df)
    except:
        pass
                                           

# In[62]:
    
# Función para obtener info de sitio de congreso
    
def info_bills_fun(tipo, i):
    if tipo == 'Congress': 
        memberdata= members_fun(tipo, i)
        info_bills = pd.DataFrame.from_dict(memberdata["results"][0]["bills"])
        info_bills['summary_sentiment'] = info_bills['summary'].apply(lambda summary:TextBlob(summary).sentiment.polarity)
        info_bills.committee_codes = info_bills.committee_codes.apply(str)
    return(info_bills)



# In[71]:
    
# Funciones para hace webscraping, descarga y parse de info a partir de pdfs de Congreso


def bills_fun(info_bills):
    bills = info_bills[info_bills.committees.isin(committees)]
    return(bills)

        
def bills_urls(tipo, i):
    if tipo == 'Congress':
        info_bills = info_bills_fun(tipo, i)
        bills = bills_fun(info_bills)
        bill_url = bills.congressdotgov_url
        urls = [ur + "/text" for ur in bill_url]
    return(urls)


############### PDFS

def pdf_content(tipo, i):
    if tipo == 'Congress':
        
        all_content = []
        
        urls = bills_urls(tipo, i)
        
        for ur in urls:
        
            print('HTTP GET: %s', ur)
            response = requests.get(ur)
        
                # parse content
            content = BeautifulSoup(response.text, 'lxml')
        
                # extract URLs referencing PDF documents
            all_content.append(content.find_all('a'))
        else:
            pass
        
        return(all_content)
    

#%% Descarga de pdfs relevantes

def pdf_download(tipo, i):
    if tipo == 'Congress':

        # loop over all URLs
        all_content = pdf_content(tipo, i)
        
        for ur in all_content:
            for url in ur:
                # try URLs containing 'href' attribute
                try:
                    # pick up only those URLs containing 'pdf'
                    # within 'href' attribute
                    if 'pdf' in url['href']:
                        # init PDF url
                        pdf_url = ''
                        
                        # append base URL if no 'https' available in URL
                        if 'https' not in url['href']:
                            pdf_url = 'https://www.congress.gov' + url['href']
            
                        # otherwise use bare URL
                        else:
                            pdf_url = url['href']
                        
                        # make HTTP GET request to fetch PDF bytes
                        print('HTTP GET: %s', pdf_url)          
                        pdf_response = requests.get(pdf_url)
                        
                        # extract  PDF file name
                        filename = unquote(pdf_response.url).split('/')[-1].replace(' ', '_')
                        
                        # write PDF to local file
                        with open(filename, 'wb') as fd:
                            # write PDF to local file
                            fd.write(pdf_response.content)
                            
                
                # skip all the other URLs
                except:
                    pass
        else:
            pass
        

#%%

## PDF Reader: Parse de info de pdfs descargados

def file_names(tipo):
        from os import walk
        
        f = []
        for (dirpath, dirnames, filenames) in walk(path):
            f.extend(filenames)
            break
        
        f = [k for k in f if 'BILLS' in k]
        
        return(f)
    
        
def parse_pdf(fname):
    with open(os.path.join(path, fname), 'rb') as ifile:
        pdf_reader = PyPDF2.PdfFileReader(ifile)
        n_pages = pdf_reader.numPages
        pages = [pdf_reader.getPage(p) for p in range(n_pages)]
        pages = [p.extractText() for p in pages]
        pages = [t.replace('\n', ' ') for t in pages]
        pages = [t.replace(r'Ł', '') for t in pages]
        pages = [t.replace(r'Š', '') for t in pages]
        pages = [t.replace(r'Æ', '') for t in pages]
        pages = [t.replace(r'00:', '') for t in pages]
        pages = [t.replace(r'\\', '') for t in pages]
        pages = [t.replace(r':', '') for t in pages]
        pages = [t.replace(r'•', '') for t in pages]
    return pages



#%%

# Desagregacion de info por enunciados por cada documento descargado

def sents_fun(f):
    prueba = []
    
    for file in f:
        prueba.append(parse_pdf(file))
    
    
    prueba2 = [] 
    
    for i in range(len(prueba)):
        prueba3 = []
        for j in range(len(prueba[i])):
            prueba3.append(nlp(prueba[i][j]))
        prueba2.append(prueba3)
        
    sents = []
    
    for s in range(len(prueba2)):
        prueba3 = []
        for j in range(len(prueba2[s])):
            prueba3.append(list(prueba2[s][j].sents))
        sents.append(prueba3)
        
    return(sents)
        

#%% Busqueda de keywords y Ancestros

# Conteno de número de menciones por keyword detectada

def mentions_fun(sents):
    
    mentions = []
    
    for b in range(len(sents)):
        mentions_aux = []
        for p in range(len(sents[b])):
            prueba3 = []
            for i in range(len(sents[b][p])):
                prueba4 = []
                for k in keywords:
                    prueba4.append([t for t in sents[b][p][i] if t.text == k])
                prueba3.append(prueba4)
            mentions_aux.append(prueba3)
        mentions.append(mentions_aux)
        
           
    mentions2 = []
    
    for m in mentions:
        mentions3 = []
        for i in m:
            for j in i:
                for k in j:
                    for l in k:
                        mentions3.append(l)
        mentions2.append(mentions3)
        
    return(mentions2)


def ancestor_fun(mentions2):
    
    mentions_ancestors = []
    for b in range(len(mentions2)):
        mentions_ancestors.append([list(t.ancestors) for t in mentions2[b] if t.is_stop == False])
    
    return(mentions_ancestors)



#%%

### Outputs

# Creación de tablas finales output para aplicación


def mentions_dict_fun(files, mentions2):
    mentions_dict= {}
    
    for fi in range(len(files)):
        #for i in range(len(mentions2)):
            mentions_dict[files[fi]] = [m for m in mentions2[fi]]
    return(mentions_dict)

def ancestors_dict_fun(files, mentions_ancestors):
    ancestors_dict= {}
    
    for fi in range(len(files)):
        #for i in range(len(mentions_ancestors)):
            ancestors_dict[files[fi]] = [m for m in mentions_ancestors[fi]] 
    return(ancestors_dict)


def token_dict_fun(files, mentions_ancestors):
    f = file_names(0)
    sents= sents_fun(f)
    mentions2 = mentions_fun(sents)
    mentions_dict = mentions_dict_fun(files, mentions2)
    token_dict = {}
    
    for fi in range(len(files)):
        token_dict[files[fi]] = {}
        for i in mentions_dict[files[fi]]:
            token_dict[files[fi]][i] = [m for sublist in mentions_ancestors[fi] for m in sublist]
    return(token_dict) 



def mentions_df_fun(files, mentions_dict, bills):
    
    mentions_df = bills[['bill_id', 'bill_slug','short_title', 'sponsor_title', 'sponsor_name', 'sponsor_party', \
                         'congressdotgov_url', 'latest_major_action_date', 'latest_major_action','summary_sentiment']]
        
    
    mentions_df = mentions_df.reset_index(drop = True)
    
    
    arr1 = [str(f) for f in files]
    
    arr2 = []
    
    for f in files:
        arr2.append([str(k) for k in mentions_dict[f]])
        
    
    aux_df = pd.DataFrame(arr1)
    
    aux_df['keywords'] = [k for k in arr2]
    
    aux_df['keyword_count'] = [len(k) for k in arr2]
    
    aux_df['pdf_file'] = aux_df[0].astype(str)
    
    
    
    
    aux = []
    for f in files:
            aux.append(re.search("(?=BILLS).*?(?=.pdf)",str(f)))  
        
    aux2 = []
    for au in aux:
        try:
            aux2.append(au.group(0))
        except:
            pass
    
    aux_df[2] = aux2
    
    
    aux_df['bill_slug'] = aux_df[2].str[9:-2]
    
    
    mentions_df = pd.merge(mentions_df, aux_df, on = "bill_slug")
    
    mentions_df = mentions_df.drop(columns=[0,2, 'bill_slug', 'pdf_file'], axis = 1)
    
    mentions_df = mentions_df.sort_values(by='keyword_count', ascending=False)
    
    mentions_df = mentions_df[mentions_df['keyword_count'] >= 1]

    return(mentions_df)



def output_table(tipo, i):
    
    if tipo == 'Political Statements':
        table_df = statement_fun(tipo, i)
        return(table_df)
    
    elif tipo == 'Congress':
        info_bills = info_bills_fun(tipo, i)
        bills = bills_fun(info_bills)
        pdf_download(tipo, i)
        f = file_names(tipo)
        sents= sents_fun(f)
        mentions2 = mentions_fun(sents)
        files = f
        mentions_dict = mentions_dict_fun(files, mentions2) 
        
        table_df = mentions_df_fun(files, mentions_dict, bills)
        
        files_in_directory = os.listdir(path)
        filtered_files = [file for file in files_in_directory]
        for file in filtered_files:
            if '.pdf' in file:
            	path_to_file = os.path.join(path, file)
            	os.remove(path_to_file)
        return(table_df)
    

def ancestors_table(tipo, i):

    if tipo == 'Congress':
        info_bills = info_bills_fun(tipo, i)
        bills = bills_fun(info_bills)
        urls = bills_urls(tipo, i)
        all_content = pdf_content(tipo, i)
        pdf_download(tipo, i)
        f = file_names(tipo)
        sents= sents_fun(f)
        mentions2 = mentions_fun(sents)
        mentions_ancestors = ancestor_fun(mentions2)
        files = f
        mentions_dict = mentions_dict_fun(files, mentions2) 
        ancestors_dict = ancestors_dict_fun(files, mentions_ancestors) 
        token_dict = token_dict_fun(files, mentions_ancestors) 
        
        files_in_directory = os.listdir(path)
        filtered_files = [file for file in files_in_directory]
        for file in filtered_files:
            if '.pdf' in file:
            	path_to_file = os.path.join(path, file)
            	os.remove(path_to_file)
        return(token_dict)


