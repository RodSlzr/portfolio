'''
This file:
    -Text cleaning
    -Cluster in categories of interest
    -Sentiment analysis

Functions: 
    -tweets_processing
    -tweets_df
    -clean_tweet
    -clean_all_tweets
    -jaccard_similarity
    -get_scores
    -tweets_clustering
    -sentiment
    
Note: We process the tweets by year otherwise python terminates 
    our code because it is too much data at one time 
'''

import numpy as np
import re
import twint
import datetime as dt 
import os 
import pandas as pd
import nest_asyncio
import glob
import shutil
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import nltk
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nest_asyncio.apply() 

stopwords = stopwords.words('english')
stopwords = set(stopwords)

save_dir = os.path.abspath(os.path.join(__file__ ,"../..")) + "/data/twitter/sentiment_disaggregated_results/"
dir = os.path.abspath(os.path.join(__file__ ,"../.."))

####### Example run #########
# import tweets_df_pro as tdp
# tdp.tweets_processing("tweets_downloads_test","tweets_output", "2017") ############# year must be a string

def tweets_processing(input_directory_name, output_filename, year):
    '''
    Function to incorporate cleaning, clustering and sentiment on all 
    tweets
    
    Inputs: input_directory_name (str): folder within /data/twitter/ where 
                you would like to pull in your twitter data 
            output_filename (str): filename you would like for your output
            year (str): year of interest, used to sort data and in your output 
                filename
            
    Output: csv saved with your output to the directory specified
    '''
    df = tweets_df(input_directory_name)
    df = df[df['date'].str.slice(stop=4) == year]
    clean_all_tweets(df)
    tweets_clustering(clust_cat, df)
    sentiment(df)
    #df.to_csv(os.path.join('./', f'{output_filename}{year}.csv'))
    #df.to_csv(save_dir, f'{output_filename}{year}.csv')
    df.to_csv(os.path.join(save_dir, f'{output_filename}{year}.csv'))



######################## Create a DataFrame of the Tweets ########################
def tweets_df(input_directory_name):
    '''
    Merge all tweets and format them 
    
    Inputs: input_directory_name (str): folder within /data/twitter/ where 
        you would like to pull in your twitter data 
         
    Output (df): all files of interest merged and with initial pre-processing 
        complete
    '''
    path = dir + f"/data/twitter/{input_directory_name}"# use your path
    all_files = glob.glob(path + "/*.csv")

    files_data = []

    for file in all_files:
        df = pd.read_csv(file, index_col=None, header=0)
        files_data.append(df)

    dframe = pd.concat(files_data, axis=0, ignore_index=True)
    dframe = dframe[['id', 'date', 'time', 'near', 'tweet']]
    dframe = dframe.set_index('id')
    dframe = dframe.drop_duplicates() 

    return dframe

######################## Cleaning section ########################

def clean_tweet(tweet):
    '''
    Function to incorporate do 'deep cleaning' on tweet - strip away 
    punctuation, emojis and take out commonly used english words
    
    Inputs: tweet (str): tweet you would like to clean 
    
    Output: cleaned tweet 
    '''
    if type(tweet) == np.float:
        return ""
    clean_tweet = tweet.lower()
    clean_tweet = re.sub("'", "", clean_tweet) # to avoid removing contractions in english
    clean_tweet = re.sub("@[A-Za-z0-9_]+","", clean_tweet)
    clean_tweet = re.sub("#[A-Za-z0-9_]+","", clean_tweet)
    clean_tweet = re.sub(r'http\S+', '', clean_tweet)
    clean_tweet = re.sub('[()!?]', ' ', clean_tweet)
    clean_tweet = re.sub('\[.*?\]',' ', clean_tweet)
    clean_tweet = re.sub("[^a-z0-9]"," ", clean_tweet)
    clean_tweet = clean_tweet.split()
    clean_tweet = [w for w in clean_tweet if not w in stopwords]
    clean_tweet = " ".join(word for word in clean_tweet)
    return clean_tweet

def clean_all_tweets(frame):
    '''
    Clean all tweets in df
    
    Inputs: frame (df): df with tweets you would like to clean in place
    
    Output: df with cleaned tweets in 'tweet' column
    '''
    frame['tweet'] = frame['tweet'].map(lambda x: clean_tweet(x))

######################## Clustering section #####################################

# Create 4 corpus' on which to base our NLP algorithm for clustering 

hate = ''' racism nigger blacky uppity sexism bitch cunt bimbo feminazi homophobia fag faggot homo black
racism racist bigotry blm caucusing blackness colonization white whites supremacist blacks poc appropiation
culture genocide diaspora anti semitic zionist jew jews discrimination superiority diversity speech ethnic
ethnicity indigenity indigenous native american english spanish language country tolerance intolerance
dominance intersectionality marginalization beans border foreign minority woman women people oppression
power prejudice race racial identity equity racialization reparations social muslim arabs chinese asian asians
nigga privilege supremacy xenophobia kkk ku klux klan pig abbie abe abie afro african colored karen
ape jemima beaner beaney bluegum bootlip brownie buddhahead indian burr ching ching coconut coon cracker
crow greaser jap jewboy nip oreo rastus sambo latinos latino wetback natzi sheeny snowflake wigger wigga
trash wop zipperhead gay lesbian lgbt queer shemale tranny trans cuntboy chic radical digger bitches slut
cougar hysteria female whore parasites nationalist nationalism patriotism misogyny mannish bitchy hate diva
frigid man-eater prude mumsy neurotic hysteria pregnant abortion rights civil tomboy catfight botchfest
sissy effeminate fear bullying bully bisexual homo homophobic limp-wristed dyke flamer sod sodomite twink
lesbo fairy poof drag pansy antipathy detest abhor disgust disgusting pussy empathy antipathy aversion
hijab camel sand hitler lynch lynching mexican
'''

guns = '''gun guns shot shoot shooting load rifle bullet target aim control regulation law misfire ballistic
firearm firearms act 1968 owners protection private property weapons assault ban second amendment national association
lives march gunowners america automatic semiautomatic caliber brady handgun mass gunman bump stocks binary
trigger pistol pistols shooters school suppressor high capacity reload killer suicide ak ak-47 ar-65 trigger
bullets bulletproof barrel machine-gun laws prohibition permit purchase unlicensed mental illness background
check records dealer registration advocates gunshot massacre columbine discharging unarmed hostage tragedy
slaughter annihilation shooter sniper marksman accident gunner piece rod heater revolver derringer fatal
fatality killed kills death headshot execution execute puller gun-owners license nra sandyhook common sense
roght bear self-defense pulse arms
'''

crimes = '''police ribber kidnap assault mug mugger mugging murder murderer killer violent crime robber
robbery attack rape rapist hurt injur victim justice aggresor hijack hijacker punch hit assasin attack
harm arrest crimes criminal abduction assassination burglar burglary homicide hooliganism theft
looting manslaughter pickpocketing trespassing lynching victim accomplice offender harrasment harras
fbi first degree felony malice aforethought unlawful kill premeditation aggravate permissive strangulation
strangulate poisoning terminatins harm detrimental punishment prison jail deliberation life sexual
pedophile pederast perpetrator abuse violence cash wallet phone laptop computer belongings money guilt
guilty larceny threat wound battery weapon gun shot knife car force intercourse gang invasion consent
ravish violate rob loot bang
'''

addictions = '''drugs alcohol tobacco smoking cigarrette cigar joint snuff addict junk disease drugging rehab
rehabilitation trafficking narco narcotics inject substance marijuana smoker rolling paper roach clip dealer
drinker social drink hallucinate hallucinogen beer cocaine coke crack coca narc hooka hash liquor liqueur pot
weed grass dope pass kilo heroin fentanyl od overdose mescaline nark size popper depressant deviant pusher
tranquilizer peyote therapy amphentanile angel dust tequila scotch whiskey gin vodka rum alcoholic anonymous
party pipe push lsd pills ecstasy tonic clean sniff line mainline cook methamphetamine meth crank steroid
pass bottom out drunkard blackout pot-head stoned dependent dependency cut columbian downer flashback
amphentamine cocktail depressant teetotaler screwdriver roll bong chug prescription prescribe pharmacist
toke symptom hangover paraphernalia bennie hypodermic caffeine habit mushrooms bar snort stimulant glue
relapse abstinence street sniff smack drunkard pill tolerance therapy champagne sober spoon opium opioid
lid bust boost booze intervention rolling abuse treatment brandy illegal crystal acid green gold
herb bash flake snow powder blue tranqs chalk health addiction hospital hospitalize hospitalise clinic
needle vessels na aa 12 steps twelve steps addicted addictive gateway
'''

clust_cat = {'hate' : hate, 'guns' : guns, 'crimes' : crimes, 'addictions' : addictions}


def jaccard_similarity(query, document):
    '''
    Calculate jaccard similarity score on a string based for a given category 
    
    Inputs: query (list): corpus of words for category
            document (str): string you want a jaccard similarity score for 
            
    Output: jaccard similarity score of tweet
    '''
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection)/len(union)

def get_scores(group,tweets):
    '''
    Calculate jaccard similarity for list of tweets
    
    Inputs: group (list): corpus of words for category
            tweet (str): tweet you want a jaccard similarity score for 
            
    Output: list of scores
    '''
    scores = []
    for tweet in tweets:
        s = jaccard_similarity(group, tweet)
        scores.append(s)
    return scores

def tweets_clustering(clust_cat, df):
    '''
    Categorize each tweet into the category with the highest 
    jaccard similarity score 
    
    Inputs: cluster_cat (dict): dictionary of categories with their corpus'
            df (df): df with tweets that you would like to categorize given 
                their scores for different categories
            
    Output: df updated in place to include categories for each tweet
    '''
    df['Score_cat'] = 0
    df['Category'] = None
    for cat, voc in clust_cat.items():
        df[cat] = get_scores(voc, df.tweet.to_list())
        df['Score_cat'] = df[['Score_cat', cat]].max(axis = 1)
        df['Category'][df['Score_cat'] == df[cat]] = cat 
        

######################## Sentiment Analysis section ########################

def sentiment(df): 
    '''
    Use VADER (a pre-trained sentiment analysis model) to categorize 
    tweets into having a positive, negative and neutral category
    
    Inputs: df (df): df with tweets for which you want the sentiment 
            
    Output: df updated in place to include sentiement for each tweet
    '''
    sid = SentimentIntensityAnalyzer() # Calculate neutral, negative and positive sentiment scores and label tweet with highest sentiment 
    df['sentiment'] = None #np.nan
    for idx, tweet in enumerate(df['tweet']):
        sentiment_dict = sid.polarity_scores(tweet)
        sentiment_names = ('Negative', 'Positive', 'Neutral')
        sentiment_tup = (sentiment_dict['neg'], sentiment_dict['pos'], sentiment_dict['neu'])
        if np.any(sentiment_tup) > 0.0: # if all values are 0, leave label as nan
            index = sentiment_tup.index(max(sentiment_tup))
            df['sentiment'].iloc[[idx]] = sentiment_names[index] 
    df['Tweets'] = df['tweet']
    df.drop(['tweet'], axis = 1, inplace = True)
