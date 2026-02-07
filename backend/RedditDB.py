import asyncio
import os
import re
import pandas as pd
import asyncpraw
from dotenv import load_dotenv
import nltk
from nltk.corpus import stopwords
import SentimentModel as sm

# 1. Setup Environment and NLTK
load_dotenv()
nltk.download('stopwords', quiet=True)
stop_words = set(stopwords.words('english'))

# 2. DON'T create reddit client here - create it lazily
reddit = None

async def get_reddit_client():
    """Lazy initialization of Reddit client within async context"""
    global reddit
    if reddit is None:
        reddit = asyncpraw.Reddit(
            client_id=os.environ.get("client_id"),
            client_secret=os.environ.get("client_secret"),
            password=os.environ.get("password"),
            user_agent=os.environ.get("user_agent"),
            username=os.environ.get("user"),
        )
    return reddit

async def getUserInfo():
    reddit_client = await get_reddit_client()
    me = await reddit_client.user.me()
    print(f"Authenticated as: {me}")
    print(f"AsyncPRAW Version: {asyncpraw.__version__}")

async def getSubredditData(subreddit_name):
    reddit_client = await get_reddit_client()
    subreddit_posts = {"title": [], "text": []}
    subreddit = await reddit_client.subreddit(subreddit_name)
    
    print(f"Fetching posts from r/{subreddit_name}...")
    async for post in subreddit.new(limit=100):
        subreddit_posts["title"].append(post.title)
        subreddit_posts["text"].append(post.selftext if post.selftext else "")
        
    return subreddit_posts

def clean_text(text):
    text = str(text)
    if text.lower() in ['[removed]', '[deleted]']:
        return ''
    
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words).strip()

async def getMentalScore(subreddit_name):
    reddit_client = None  # Initialize to None
    try:
        reddit_client = await get_reddit_client()
        raw_data = await getSubredditData(subreddit_name)
        df = pd.DataFrame(raw_data)

        if df.empty:
            print("No data retrieved.")
            return 0.0

        df['cleaned_text'] = (df['title'] + ' ' + df['text']).apply(clean_text)
        print("Calculating scores...")
        
        df['scores'] = await asyncio.to_thread(
            lambda: df['cleaned_text'].apply(sm.SentimentOnSubreddit)
        )
        
        df['compound_score'] = df['scores'].apply(lambda d: d.get("compound", 0))
        mental_health_score = float(df['compound_score'].mean())
        print(f"Subreddit Score: {mental_health_score}")

        await asyncio.to_thread(df.to_csv, 'SubredditData.csv', index=False)
        
        return mental_health_score

    except Exception as e:
        print(f"Error in getMentalScore: {e}")
        raise e
    finally:
        # IMPORTANT: Close the client after each request
        if reddit_client is not None:
            await reddit_client.close()
        # Reset global so next request creates fresh client
        global reddit
        reddit = None
        
async def main():
    try:
        await getUserInfo()
        await getMentalScore("UMD")
    finally:
        if reddit is not None:
            await reddit.close()

if __name__ == "__main__":
    asyncio.run(main())