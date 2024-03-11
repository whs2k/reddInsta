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
#time.sleep(sleep_time)

print('num of arguments: ', len(sys.argv))
#print(sys.argv)
input_args = sys.argv

list_of_subreddits = ['blowjobsandwich',
					'CumCoveredSluts','BabeCock','GirlsFinishingTheJob','cumsluts',
					'nsfwcosplay', 'deepthroat','Bukkake_Before_After','bukkake','PornIsCheating','pornrelapsed',
					'bigtitsinbikinis','SpitRoasted','ClassyPornstars',
					'ModelsGoneMild','tiktokthots','Exxxtras','Oilporn','HENTAI_GIF','blowbang',
					'Licked','xxxcaptions','porninfifteenseconds',
					'hentai','Futanari','FutanariGifs','futanari_Comics','FutanariHentai','Pornstar_moms'] 
					#'BimboFetish','javdreams','deepthroat','ActuallyHugeCumshots','FemboyHentai',
star_subreddits = ['AngelaWhite','Miakhalifa','RileyReid','MiaMalkova','GabbieCarter','abelladanger',
				   'AdrianaChechik','LenaPaul','RemyLaCroix','Sashagrey','Eimi_Fukada','DreddxxxOnly',
				   'GiannaMichaels','BrandiLove','sophiedee','LisaAnn','JadaStevens', 'VioletMyers',
				   'KendraLust','valentinanappi','karleegrey','MandyMuse','Evalovia','AlettaOcean__',
				   'SaraJay','NicoletteSheaNew','KristyBlack','NatashaNice','KahoShibuya','SyrenDeMer',
				   'ClubDeeWilliams','ValericaSteele','chloe_cherry','GiaDerza_X','AshleyAdams',
				   'BriannaArson','KiannaDior','JasmineJaeXX','MarshaMay','BreeOlson','Alexis_Fawx',
				   'MikeAdriano','charlottesartre']
				   
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
today_str = str(datetime.datetime.now().date())
tommorrow_str = str(datetime.date.today() + datetime.timedelta(days=1))
with open ('todays_list.ob', 'rb') as fp:
	todays_alreadysent_list = pickle.load(fp)
	#print(todays_alreadysent_list)
if today_str in todays_alreadysent_list:
	pass
else:
	todays_alreadysent_list = [today_str, tommorrow_str]

filename = 'to_upload.mp4'

while not os.path.isfile(filename):
	subreddits_to_choose_from = [x for x in all_subreddits if x not in todays_alreadysent_list]
	subreddit = random.choice(star_subreddits)
	print(subreddit)
	for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
		#print(x.url)
		if ('redgifs' in x.url) & (str(x.title) not in todays_alreadysent_list):
			url = x.url
			print(url, flush=True)
			video_url = helper.get_redgifs_embedded_video_url(redgifs_url=url,output_fn=filename)
			#print(tweet_title, flush=True)
			break
	todays_alreadysent_list.append(subreddit)
	todays_alreadysent_list.append(str(x.title))
	with open('todays_list.ob', 'wb') as fp:
		#pickle.dump([], fp)
		pickle.dump(todays_alreadysent_list, fp)
tweet_title=str(x.title).replace('my','the').replace('I','they').replace("I'm","they're") \
					.replace("I've","they've").replace("I'd","they'd").replace(' me ','them').replace(' Me ','Them')
if subreddit in star_subreddits:
	tweet_title = tweey_title + ' #' +str(subreddit).replace('_','').replace('X','') \
		.replace('Club','').replace('New','')
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


