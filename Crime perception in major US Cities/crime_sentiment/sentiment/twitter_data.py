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

from calendar import month
import twint
import datetime as dt 
import os 
import pandas as pd
import nest_asyncio
import glob
import shutil
import time
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
nest_asyncio.apply()

# Parameters:
save_dir = os.path.abspath(os.path.join(__file__ ,"../..")) + "/data/twitter/"
cities = ["new york city", "los angeles", "chicago", "houston", "phoenix",
"san antonio", "philadelphia", "san diego", "dallas", "austin"]
# Directory to test this function without affecting the data we used for
# our analysis:
dir_for_tweets = "tweets_downloads_test"

# Vocabularies
viol_voc_1 = '''violence violent crime shooting gun murder
assault rape harassment terrorist terrorist
racist robber arrest supremacist sexist
attack trafficking homophobia misogyny injured
weapon narco pedophile abuse victim
danger brutal assassin attack
protest extremist harm rage threat
anger retaliate'''

viol_voc_2 = '''bloody dead deadly death assassinate
ammunition fatal  bullet assault aggressor
dispute brutality ambush hijack hijacker
rape rapist raped victim punch
punched kick stab
weapon knife wound hurt wounded
offense kidnap kidnapped kidnapping abuse
aggressive force suicide bully riot'''

viol_voc = [viol_voc_1, viol_voc_2]
# We kept some words out because they were creating a lot of noise, like:
# hate terrified hit die scared fear force blood

def tweets_scraping(vocabulary, day1, month1, year1, day2, month2, year2):
    '''
    Scrapes tweets that contain words in the vocabulary during a given period
    of time.
    
    Inputs:
        vocabulary(list of strings): List of strings to search in twitter.
        A list is used to expand the words we can search as twitter limits
        the number of words to filter every search.
        day1, month1, year1 (int): day, month and year to begin the search.
        day2, month2, year2 (int): day, month and year to stop the search.

    Output:
        CSV files that contain the tweet scraped by city, vocabulary and day.

    '''
    start_date = dt.datetime(year1, month1, day1)
    end_date = dt.datetime(year2, month2, day2)
    for ind_voc, voc in enumerate(vocabulary):
        search_term = vocabulary_to_search(voc)
        # Loop through cities
        for city in cities:
            twint_search_loop(search_term, start_date, end_date, city, ind_voc)


def vocabulary_to_search(vocabulary):
    '''
    Prepares the vocabulary to be in the proper format for a twitter
    search 
    
    Inputs:
        vocabulary(list of strings): List of strings to search in twitter.

    Output:
        voc_split_or(string): String with the right format.

    '''
    voc_split = vocabulary.split()
    voc_split_or = " OR ".join(voc_split)
    return voc_split_or


def twint_search_loop(search_term, start_date, end_date, city, ind_voc):
    '''
    Scrapes tweets by date.
    
    Inputs:
        search_term(strings): Words to search in twitter.
        A list is used to expand the words we can search as twitter limits
        the number of words to filter every search.
        start_date (date): Date to begin the search.
        end_date (date): Date to stop the search.
        city (string): City where the tweets are scraped
        ind_voc (ind): Indicates what vocabulary is it using for scraping

    Output:
        CSV files that contain the tweet scraped by city, vocabulary and day.

    '''
    try:
        os.makedirs(os.path.join(os.getcwd(),save_dir, dir_for_tweets))
        print(f'Successfully created the directory {os.path.join(os.getcwd(),save_dir,search_term)}')
    except FileExistsError:
        print(f'Directory {os.path.join(os.getcwd(),save_dir, dir_for_tweets)} already exists')
    
    date_range = pd.date_range(start_date, end_date)
    
    for single_date in date_range:
        since = single_date
        until = single_date + dt.timedelta(days = 2)
        save_path = os.path.join(save_dir, dir_for_tweets, f'{single_date:%Y%m%d}{city}{ind_voc}.csv')
        if not os.path.exists(save_path):
        #print(save_path)
            print(f"Searching for tweets containing '{search_term}' from {single_date:%Y-%m-%d} and saving into {save_path}")
            twint_search(search_term, since, until, save_path, city)


def twint_search(search_term, since, until, save_path, city):
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
    c.Search = search_term
    c.Lang = "en"
    c.Near = city
    c.Limit = 2000000
    c.Pandas = True
    c.Since = since.strftime('%Y-%m-%d %H:%M:%S')
    c.Until = until.strftime('%Y-%m-%d %H:%M:%S')
    c.Hide_output = True
    c.Popular_tweets = True
    c.Filter_retweets = True
    c.Store_csv = True
    c.Output = save_path
    twint.run.Search(c)

