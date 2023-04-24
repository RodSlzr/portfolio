#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 09:51:17 2021

@author: javiergutierrez
"""

# Carga de librerías

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
import function
import media_unidos
import commerce_news
from IPython.display import HTML
from pretty_html_table import build_table


########## APP BUSCADOR USMCA

app = Flask(__name__)


SOURCES = [
    "Congress",
    "Political Statements",
    "News & Media"
    "Commerce"
    ]


headers = {'X-API-Key': 'Qoc26kX4ASSpatIYaMhAAtk4RFYlO24gb2Z8VZZW'}



@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        if request.form.get("source") == 'Commerce':
            tabla_csv = commerce_news.run_all()
            tabla_csv.to_csv('tabla.csv', index = False)
            html_table = build_table(tabla_csv, 'green_dark')
            return html_table
        
        if request.form.get("source") == 'News & Media':
            tabla_csv = media_unidos.run_all(request.form.get("name"))
            tabla_csv.to_csv('tabla.csv', index = False)
            html_table = build_table(tabla_csv, 'green_dark')
            return html_table
            
        else:
                tabla_csv = function.output_table(request.form.get("source"), request.form.get("name"))
                tabla_csv.to_csv('tabla.csv', index = False)
                html_table = build_table(tabla_csv, 'green_dark')
                return html_table
        

if __name__ == '__main__': 
    app.run(debug = True)
    

    
    
    
    