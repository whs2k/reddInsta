from pytwitter import Api
import math
import praw #for reddit
import requests
import datetime
import random
import os
import time
import shutil
import traceback
import sys
import pickle
sleep_time = random.choice(range(1000))
print(sleep_time, flush=True)
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

with open ('todays_list.ob', 'rb') as fp:
	todays_alreadysent_list = pickle.load(fp)
	print(todays_alreadysent_list)
if datetime.datetime.today in todays_alreadysent_list:
	pass
else:
	todays_alreadysent_list = [datetime.datetime.today]

filename = 'to_upload.gif'

subreddits_to_choose_from = [x for x in all_subreddits if x not in todays_alreadysent_list]
subreddit = random.choice(subreddits_to_choose_from)
print(subreddit)
for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
	#print(x.title)
	#print(x.url)
	if '.gifv' in x.url:
		continue
	elif '.gif' in x.url:
		print(x.title)
		print(x.url)
		with open(filename, "wb") as f: # opening a file handler to create new file 
			f.write(requests.get(x.url).content) # writing content to file
			tweet_title=str(x.title).replace('my','the').replace('I','they').replace("I'm","they're") \
				.replace("I've","they've").replace("I'd","they'd") + ' #' +str(subreddit)
		break

if not os.path.isfile(filename):
	for x in reddit.subreddit(subreddit).top(time_filter='day',limit=10):
		if 'redgifs' not in x.url:
			filename = x.url.split('/')[-1]
			with open(filename, "wb") as f: # opening a file handler to create new file 
					f.write(requests.get(x.url).content) # writing content to file
					tweet_title=str(x.title).replace('my','the').replace('I','they').replace("I'm","they're") \
						.replace("I've","they've").replace("I'd","they'd") + ' #' +str(subreddit)
			break

todays_alreadysent_list.append(subreddit)
with open('todays_list.ob', 'wb') as fp:
	#pickle.dump([], fp)
	pickle.dump(todays_alreadysent_list, fp)

try:
	with open(filename, "rb") as media:
		resp = twitter_api_authorized.upload_media_simple(media=media)
		print(resp)
	twitter_api_authorized.create_tweet(
		text=tweet_title,
		media_media_ids=[str(resp.media_id)])
except Exception:
	print(traceback.format_exc())
	pass
os.remove(filename)

