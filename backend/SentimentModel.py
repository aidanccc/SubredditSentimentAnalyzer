import pandas as pd
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm import tqdm

sia = SentimentIntensityAnalyzer()


def SentimentOnSubreddit(text):
    '''
    res = {}
    for i, row in tqdm(df.iterrows(), total=len(df), miniters=100):
        text = row['cleaned_text']
        myid = row['id']
        res[myid] = sia.polarity_scores(text)
    '''
    return sia.polarity_scores(text)
'''
df = pd.read_csv("amazon_reviews/Reviews.csv")

res = {}
for i, row in tqdm(df.iterrows(), total=len(df), miniters=100):
    text = row['Text']
    myid = row['Id']
    res[myid] = sia.polarity_scores(text)
'''

UMD = SentimentOnSubreddit("amazon_reviews/Reviews.csv")
print(UMD)
#vaders = pd.DataFrame(res)
#print(vaders)
# vaders = vaders.reset_index().rename(columns={'index': 'Id'})
# vaders = vaders.merge(df, how="left")
