import sys
#import helper
import traceback
from pytwitter import Api
import math
import praw #for reddit
import requests
import datetime
import random
import os
import time
import pickle
import helper

sleep_time = random.choice(range(3000))
print('sleep time: ', sleep_time, flush=True)
time.sleep(sleep_time)

print('num of arguments: ', len(sys.argv))
#print(sys.argv)
input_args = sys.argv

list_of_subreddits = ['ModelsGoneMild','gentlemanboners',
'PrettyGirls','BeautifulFemales','ClassyPornstars']
#,'nonnude','2busty2hide']
length = len(list_of_subreddits)

hour = datetime.datetime.now().hour
if 13 <= hour < 15:
    index=0
elif 15 <= hour < 17:
    index=1
elif 17 <= hour < 19:
    index=2
elif 19 <= hour < 21:
    index=3
elif 21 <= hour < 23:
    index=4




subreddit = list_of_subreddits[index]

reddit = praw.Reddit(client_id=input_args[1], #REDDIT_CLIENT_ID
					 client_secret=input_args[2],#REDDIT_CLIENT_SECRET
					 password=input_args[3], #REDDIT_PASSWORD
					 user_agent=input_args[4], #REDDIT_USER_AGENT
					 username=input_args[5] #REDDIT_USER_NAME
					 )
twitter_api_authorized = Api(
		access_token=input_args[6], #TWITTER_ACCESS_TOKEN,
		access_secret=input_args[7], #TWITTER_ACCESS_TOKEN_SECRET
		client_id = '1774458519154286592',
		consumer_key = input_args[8], #TWITTER_CONSUMER_KEY
		consumer_secret = input_args[9], #TWITTER_CONSUMER_SECRET
	oauth_flow=True
	)

fn_to_upload = 'to_upload.jpg'
#print(subreddit)
while not os.path.isfile(fn_to_upload):
    print(subreddit)
    for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
        print(x.url)
        if (('jpeg' in x.url) | ('jpg' in x.url)):
            url = x.url
            print(url, flush=True)
            r = requests.get(url)
            with open(fn_to_upload,"wb") as f:
                f.write(r.content)
            break
    original_title = str(x.title).replace(' [irtr]','').replace(' [IRTR]','') \
    						.replace('[irtr]','').replace('[IRTR]','')

if original_title.count(' ') == 1:
	original_title = '#' +  original_title.replace(' ','')


fn_format = fn_to_upload.split('.')[-1]
total_bytes = os.path.getsize(fn_to_upload)
print(total_bytes)



resp = twitter_api_authorized.upload_media_chunked_init(
	total_bytes=total_bytes,
	media_type="image/"+fn_format,
)
media_id = resp.media_id_string
#print(media_id)

segment_id = 0
bytes_sent = 0
file = open(fn_to_upload, 'rb')
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


time.sleep(10)
#resp = api_authorized.upload_media_chunked_status(media_id=media_id)
#print(resp)

tweet_text_final = helper.convert_hastag_to_at(original_title)


twitter_api_authorized.create_tweet(
	text=tweet_text_final,
	media_media_ids=[media_id]
)
print(tweet_text_final)
os.remove(fn_to_upload)
