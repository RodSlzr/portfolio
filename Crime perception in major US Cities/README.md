# Crime Data & Twitter Analysis by Major US Cities, 2005-2021
### By Rodrigo Salazar, Sophie Logan, Kenia Nogueda, & Alejandro Saenz

### You can read [here](https://github.com/RodSlzr/portfolio/blob/main/Crime%20perception%20in%20major%20US%20Cities/Capptivators%20Paper%20(1).pdf) the results of the project.

## Description

This project explores whether violent sentiment in a city, as represented by tweets, has any correlation with actual crimes in that city and whether that relationship changes over time. We combined tweets containing violent language with FBI data on crimes in the largest US cities from 2005-2021. The dashboard aims to visually display (time and cross-sectional) trends of violent sentiment on twitter and actual crimes to help to discover patterns that relate both sources of data.
Data is disaggregated by type of crime, using FBI categories, and twit category, which was constructed using clustering analysis by topic in Twitter. We used both sentiment analysis (VADER) and clustering techniques (jaccard similarity) to categorize tweets by attitude and category under the umbrella of violent language. This analysis could be a helpful indicator in understanding whether violent sentiment is a lagging or leading indicator of actual crimes and whether a city can change challenging problems both culturally in the way people speak to one another and in terms of actual crime rates.

## Technologies used
Pandas, NumPy, NLTK, Scikit-learn, Twint, Dash, and Plotly.

### To run the app: 

(1) Enter the virtual environment while you are in the proj-capptivators folder by running: source install.sh 

(2) Enter into the crime_sentiment folder 

(3) From the crime_sentiment folder, run: python3 -m crime_sentiment

(4) Dashboard will display on http://127.0.0.1.8051/


To *just* scrape tweets:

Use: twitter_data.tweets_scraping(twitter_data.viol_voc, day1, month1, year1, day2, month2, year2)

(1) import twitter_data

(2) twitter_data.tweets_scraping(td.viol_voc, 1, 1, 2017, 4, 1, 2017)



Structure of the app: 

-crime_sentiment (Code)
    
    -dashboard

        -crime.py

    -data

        -fbi

            -Crime_2000_2018.zip

        -twitter

            -aggregated_results

            -sentiment_disaggregated_results

            -tweets_downloads

            -tweets_downloads_test

        -fbi_twitter_merge

            -crime_data.csv

    -sentiment

        -twitter_data.py

        -twitter_df_pro.py

        -aggregation.py


-__init__.py

-__main__.py

-Capptivators Paper (results)

-proj-structure (diagram)

-app.py    
    
install.sh

README.md - this file

requirements.txt


