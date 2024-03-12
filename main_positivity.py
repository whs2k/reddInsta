from pytwitter import Api
import praw #for reddit
import requests
import datetime
import random
import os
import time
import sys
from redvid import Downloader
import shutil

input_args = sys.argv

reddit = praw.Reddit(client_id=input_args[1], #REDDIT_CLIENT_ID
					 client_secret=input_args[2],#REDDIT_CLIENT_SECRET
					 password=input_args[3], #REDDIT_PASSWORD
					 user_agent=input_args[4], #REDDIT_USER_AGENT
					 username=input_args[5] #REDDIT_USER_NAME
					 )
twitter_api_authorized = Api(
		access_token=input_args[6], #TWITTER_ACCESS_TOKEN_POS,
		access_secret=input_args[7], #TWITTER_ACCESS_TOKEN_SECRET_POS
		client_id = '1765940484424486912',
		consumer_key = input_args[8], #TWITTER_CONSUMER_KEY_POS
		consumer_secret = input_args[9], #TWITTER_CONSUMER_SECRET_POS
	oauth_flow=True
	)

list_of_subreddits = ['aww','MadeMeSmile','BeAmazed']
hour = datetime.datetime.now().hour
if 0 <= hour < 8:
    index=0
elif 8 <= hour < 16:
    index=1
elif 16 <= hour < 24:
    index=2


subreddit = list_of_subreddits[index]
for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
    print(subreddit)
    print(x.url)
    try:
        if '.mp4' in x.media['reddit_video']['fallback_url']:
            mp4_url = x.media['reddit_video']['fallback_url']
            #url = x.url
            #print(url)
            print(mp4_url)
            #with open(filename, "wb") as f: # opening a file handler to create new file 
            #    f.write(requests.get(mp4_url).content) # writing content to file
            reddit = Downloader(max_q=True)
            reddit.url = x.url
            reddit.download()
            time.sleep(30)
    except:
        continue
    break
tweet_title=str(x.title) + ' #' + str(subreddit)
tweet_title = tweet_title.replace('my','their').replace('I ','they').replace("I'm","they're") \
				.replace("I've","they've").replace("I'd","they'd").replace('our','their')

for item in os.listdir( os.getcwd() ):
    print(item)
    if item.endswith(".mp4"):
        filename = item
print(filename)
total_bytes = os.path.getsize(filename)
print(total_bytes)
resp = twitter_api_authorized.upload_media_chunked_init(
    total_bytes=total_bytes,
    media_type="video/mp4",
)
media_id = resp.media_id_string
print(media_id)
segment_id = 0
bytes_sent = 0
file = open(filename, 'rb')
idx=0
while bytes_sent < total_bytes:
    chunk = file.read(4*1024*1024)
    status = twitter_api_authorized.upload_media_chunked_append(
            media_id=media_id,
            media=chunk,
            segment_index=idx
        )
    idx = idx+1
    
    bytes_sent = file.tell()
    print(idx, media_id, status, bytes_sent)


resp = twitter_api_authorized.upload_media_chunked_finalize(media_id=media_id)
print(resp)
time.sleep(5)
resp = twitter_api_authorized.upload_media_chunked_status(media_id=media_id)
print(resp)
twitter_api_authorized.create_tweet(
    text=tweet_title,
    media_media_ids=[media_id],
)
shutil.rmtree('redvid_temp')
for item in os.listdir( os.getcwd() ):
    if item.endswith(".mp4"):
        os.remove( os.path.join( item ) )