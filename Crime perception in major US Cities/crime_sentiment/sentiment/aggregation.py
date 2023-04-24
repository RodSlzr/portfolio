import pandas as pd
import os

def aggregator(file): 
    '''
    Aggregates the twitter cluster and sentiment analysis by city 
    
    Input: 
        file (csv): csv with all the data from twitter, the cluster 
            and sentiment analysis 
      
    Output (csv): csv of aggregates
    '''
    df = pd.read_csv(file) 
    grouped_df = df.groupby(["near", "Category", "sentiment"])#['jaccard sim score']
    results = grouped_df.count()
    final = results[['Score_cat']]
    final.to_csv(os.path.join('./', f'results2017.csv'))
