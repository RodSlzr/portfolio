'''
This file:
    -Scrape tweets

Functions:
    -tweets_scraping: 
    -vocabulary_to_search
    -twint_search_loop
    -twint_search

Note: The scraping is done by city, vocabulary and day for the next reasons:
    city: Improve the representation of the tweets from every city despite
    their large population size differences.
    vocabulary: Overcome Twitter limitation in the words filtered per search.
    day: Overcome Twitter attempts to block twint seraches. Performing searches
    by day allow us to save the data more regularly.

'''

#from calendar import month
import twint
import feedparser
from bs4 import BeautifulSoup
# pip3 install --upgrade -e git+https://github.com/twintproject/twint.git@origin/master#egg=twint
#import datetime as dt 
#import os 
#import pandas as pd
#import nest_asyncio
#import glob
#import shutil
#import time
#from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
#nest_asyncio.apply()

keywords = ['agriculture','antidumping','api','auto','automotive','avocado','back end',
            'batteries','bea','beef','berries','border','budget reconciliation',
            'buy america','buy american','canada','china','chips','clouthier',
            'competitiveness','cool','corn','department of agriculture','department of commerce',
            'department of energy','domestic content','domestic manufacturing','domestic production',
            'dumping','ebrard','electric vehicle','electronics','energy consultations','export market',
            'export','foreign direct investment','global trade','gmo','grain oriented steel','ict','import',
            'incentive','Inflation Reduction Act','infrastructure bill','infrastructure plan',
            'international trade','investment','itc','jamie White','katherine tai','Katherine Tai',
            'labeling','machinery','made in America','manufacturing','maquiladora','marty walsh','medical device',
            'medical equipment','mexico','méxico','midterm elections','nafta','nearshoring','nec','offshoring',
            'origin','pharmaceutical','pork','potatoe','predatory prices','presidential elections',
            'protect american','protect national','raimondo','retaliation','rules of origin','seasonality',
            'section 201','section 232','section 301','section 332','semiconductor','small business administration',
            'solar panel','soybeans','steel','subsidies','substantial transformation','sugar','supply chains','tariff',
            'tariffs','tomato','tomatoes','trade agreement','trade','trading partner','unfair trade practices','unregulated fishing',
            'usda','usmca','uyghur','vaquita marina','vehicles','vilsack','world trade organization','wto']

''' Previous list:
['american jobs','buy america','cool','canada','china','department of agriculture','department of commerce']#,

            'department of energy','foreign direct investment','international trade','mexico',
            'nafta','section 201','section 232','section 301','section 332','trade','trade agreement',
            'usmca','vaquita marina','world trade organization',
            'agriculture','american-made','antidumping','api','auto','automobile','automotive','back end',
            'batteries','bea','beef','berries','budget reconciliation','build back better',
            'chips','clouthier','commerce','competition',
            'competitive business','competitiveness','corn','cotton','doc',
            'doe','dol','domestic','domestic manufacturing','domestic production','dot','dumping','ebrard',
            'electric vehicle','export','fertilizer','foreign','front end','global trade',"gmo's",
            'grain oriented steel','granholm','guzman','import tax','import','incentive',
            'infrastructure bill','infrastructure plan','itc','katherine tai','labeling',
            'machinery','manufacture','maquila','maquiladora','market','medical device',
            'medical equipment','mexico', 'méxico', 'mineral fuels','nearshoring','nec','nom','oce','offshoring',
            'origin','personal protection equipment','pharmaceutical','picte','pork','potatoe','ppe',
            'protect american','protect national','raimondo','regulations','regulator','retaliation',
            'roundup','rubber', 'semiconductor','shortage','solar panel','soybeans','steel','strengthening america',
            'subsidies','substantial transformation','sugar', 'supply chains','tai','tariff',
            'tariffs','tomato','tomatoe','small business administration','turtle excluded device','unregulated fishing','usda',
            'usica','uyghur','vehicles','vilsack','walsh','wto', 'nafta']
'''


def twint_search(tw_acc, keyword):
    '''
    Search in twitter with twint.
    
    Inputs:
        search_term(strings): Words to search in twitter.
        since (date): Date to begin the search.
        until (date): Date to stop the search.
        save_path (string): path to save the tweets scrapped.
        city (string): City where the tweets are scraped

    Output:
        CSV files that contain the tweet scraped by city, vocabulary and day.
    '''
    c = twint.Config()
    #if tw_acc:
    c.Username = tw_acc
    #print("".join(("\"", keywork, "\"")))
    c.Search = "".join(("\"", keyword, "\""))
    #"".join(("\"american jobs\"", ' OR ', "\"country of origin\"", ' OR ', "\"domestic manufacturing\"", ' OR ', 
    #"\"department of commerce\"", ' OR ', "\"department of energy\"", ' OR ', "\"foreign direct investment\"", ' OR ', 
    #"\"international trade\"", ' OR ', "\"trade agreement\"", ' OR ', "\"world trade organization\""))###, ' OR ',
    #"\"protect american\"", ' OR ', "\"supply chains\"", ' OR ', "\"pharmaceutical ingredients\"", ' OR ',
    #"\"vaquita marina\"", ' OR ', "\"offshoring\"", ' OR ', "\"production\"", ' OR ',
    #'''Mexico OR México OR USMCA OR NAFTA OR canada OR china OR agriculture OR dumping OR commerce OR manufactur'''))

    #c.Lang = "en"
    #c.Translate = True
    #c.TranslateDest = "sp"
    #c.Near = city
    c.Limit = 30
    ###c.Pandas = True
    c.Store_object = True
    #c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
    #c.Until = until.strftime('%Y-%m-%d %H:%M:%S')
    c.Hide_output = True
    ###c.Popular_tweets = True
    ###c.Filter_retweets = True
    # c.Store_csv = True
    #c.Output = save_path
    twint.run.Search(c)
    tweets = twint.output.tweets_list
    #tweets_list = []
    #for tweet in tweets:
    #    tweet_ext = tweet.datestamp + ' Usuario: ' + tweet.username + ' Tweet: ' + tweet.tweet + ' Link: ' + tweet.link
    #    tweets_list.append(tweet_ext)
    #return tweets_list
    return tweets

def twint_full_search(tw_acc, num_tweets):
    #full_tweets = []
    for keyword in keywords:
        #full_tweets += twint_search(tw_acc, keyword)
        tweets = twint_search(tw_acc, keyword)
        #print(full_tweets)
    tweets_formated = set()
    for tweet in tweets:
        if tweet.username.upper() == tw_acc.upper():
            tweet_ext = tweet.datestamp + ' Usuario: ' + tweet.username + ' Tweet: ' + tweet.tweet + ' Link: ' + tweet.link
            tweets_formated.add(tweet_ext)
    tweets_formated = list(tweets_formated)
    return sorted(tweets_formated, reverse=True)[:num_tweets]

#lst = ["2016-10-25 Usuario: repadams Tweet: ICYMI: I'll be in East Spencer tomorrow to announce a USDA Rural Development grant awarded to the city.   https://t.co/K4W5x1dVFN @WBTV_News Link: https://twitter.com/RepAdams/status/790946025808756736", '2016-10-20 Usuario: repadams Tweet: .@USDA seeks its next round of applications for Food Insecurity Nutrition Incentive (FINI) Program Grants. Apply:  https://t.co/ytpQgbPXS6 Link: https://twitter.com/RepAdams/status/789172083678859264', '2022-08-09 Usuario: repadams Tweet: Auto theft is on the rise in Charlotte as the value of vehicles increases. Please lock your vehicle, keep valuables in your home, and don’t forget to keep your car keys with you. Link: https://twitter.com/RepAdams/status/1557098327203774464']
#print(sorted(lst, reverse=True)[:2])

#tw_acc = 'RepAdams'

#print(twint_full_search(tw_acc, 25))

def rss_news_parser(cp_rss):
    if cp_rss is None:
        return []
    news = []
    NewsFeed = feedparser.parse(cp_rss)
    #print(len(NewsFeed.entries))
    for entry in NewsFeed.entries:
        
        new = entry.published[:-5] # Fecha
    
        summ_soup = BeautifulSoup(entry.summary, "html.parser")
        divs = summ_soup.findAll('div')
        print_summ = 0
        print_link = 0
        summary = 'NA'
        link = 'NA'
        for d in divs:
            if print_summ == 1:
                summary = d.getText().strip()
            if d.getText().strip() == 'Summary':
                print_summ = 1
            else:
                print_summ = 0

            if print_link == 1:
                link = d.find('a', href = True)['href']
            if d.getText().strip() == 'Link':
                print_link = 1
            else:
                print_link = 0
        new += ' | Título: ' + entry.title + ' | Resumen: ' + summary + ' | Link 1: ' + link + ' | Link 2: ' + entry.link
        news.append(new)
    return news

#cp_rss = 'https://adams.house.gov/rss.xml'
#cp_rss = 'https://aderholt.house.gov/rss.xml'

#print(rss_news_parser(cp_rss))

