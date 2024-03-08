import sys
#import helper
import traceback
from pytwitter import Api
import math
import praw #for reddit
#import requests
import datetime
import random
import os
import time
import pickle
import helper

sleep_time = random.choice(range(3300))
print('sleep time: ', sleep_time, flush=True)
time.sleep(sleep_time)

print('num of arguments: ', len(sys.argv))
#print(sys.argv)
input_args = sys.argv

list_of_subreddits = ['hentai','Futanari','FutanariGifs','futanari_Comics','FutanariHentai','blowjobsandwich',
                    'MikeAdriano','GirlsFinishingTheJob','cumsluts','javdreams','nsfwcosplay', 'deepthroat',
                     'bukkake','PornIsCheating','pornrelapsed','bigtitsinbikinis','ActuallyHugeCumshots','SpitRoasted',
                     'ClassyPornstars','ModelsGoneMild','tiktokthots','Exxxtras','Oilporn','HENTAI_GIF','FemboyHentai']
star_subreddits = ['AngelaWhite','RileyReid','MiaMalkova','GabbieCarter','abelladanger',
                   'AdrianaChechik','LenaPaul','RemyLaCroix','Sashagrey','anriokita',
                   'GiannaMichaels','BrandiLove','sophiedee','LisaAnn','JadaStevens',
                   'KendraLust','valentinanappi','karleegrey','MandyMuse','Evalovia','AlettaOcean',
                   'SaraJay','NicoletteSheaNew','KristyBlack','NatashaNice']
all_subreddits = list_of_subreddits+star_subreddits

reddit = praw.Reddit(client_id=input_args[1], #REDDIT_CLIENT_ID
					 client_secret=input_args[2],#REDDIT_CLIENT_SECRET
					 password=input_args[3], #REDDIT_PASSWORD
					 user_agent=input_args[4], #REDDIT_USER_AGENT
					 username=input_args[5] #REDDIT_USER_NAME
					 )
twitter_api_authorized = Api(
		access_token=input_args[6], #TWITTER_ACCESS_TOKEN,
		access_secret=input_args[7], #TWITTER_ACCESS_TOKEN_SECRET
		client_id = '1712104648881192960',
		consumer_key = input_args[8], #TWITTER_CONSUMER_KEY
		consumer_secret = input_args[9], #TWITTER_CONSUMER_SECRET
	oauth_flow=True
	)
#red_gifs_api = redgifsAPI() #redgifs.API()
#time.sleep(2)
#red_gifs_api.login()

with open ('todays_list.ob', 'rb') as fp:
    todays_alreadysent_list = pickle.load(fp)
    print(todays_alreadysent_list)
if datetime.datetime.today in todays_alreadysent_list:
    pass
else:
    todays_alreadysent_list = [datetime.datetime.today]

filename = 'to_upload.mp4'

subreddits_to_choose_from = [x for x in all_subreddits if x not in todays_alreadysent_list]
subreddit = random.choice(subreddits_to_choose_from)
print(subreddit)
for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
	print(x.url)
	if 'redgifs' in x.url:
		url = x.url
		print(url, flush=True)
		#resp = requests.get(url) # making requests to server
		#with open(filename, "wb") as f: # opening a file handler to create new file 
		#    f.write(resp.content) # writing content to file
		#red_gifs_api.download(url, filename)

		video_url = helper.get_redgifs_embedded_video_url(redgifs_url=url,output_fn=filename)
		
		tweet_title=str(x.title).replace('my','the').replace('I','they').replace("I'm","they're") \
                .replace("I've","they've").replace("I'd","they'd") + ' #' +str(subreddit)
		#print(tweet_title, flush=True)
		break
tweet_title=str(x.title).replace('my','the').replace('I','they').replace("I'm","they're") \
                .replace("I've","they've").replace("I'd","they'd") + ' #' +str(subreddit)

todays_alreadysent_list.append(subreddit)

with open('todays_list.ob', 'wb') as fp:
    #pickle.dump([], fp)
    pickle.dump(todays_alreadysent_list, fp)

total_bytes = os.path.getsize(filename)
print(total_bytes)
resp = twitter_api_authorized.upload_media_chunked_init(
    total_bytes=total_bytes,
    media_type="video/mp4",
)
media_id = resp.media_id_string
#print(media_id)

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


time.sleep(10)
resp = twitter_api_authorized.upload_media_chunked_status(media_id=media_id)
print(resp)

twitter_api_authorized.create_tweet(
	text=tweet_title,
	media_media_ids=[media_id]
)

os.remove(filename)


