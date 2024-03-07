import sys
#import helper
import traceback
from pytwitter import Api
from moviepy.editor import VideoFileClip
import math
import praw #for reddit
#import requests
import redgifs
import datetime
import random
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import time
import shutil

print('num of arguments: ', len(sys.argv))
#print(sys.argv)
input_args = sys.argv

list_of_subreddits = ['MikeAdriano','AngelaWhite',
                      'girlsfinishing','cumsluts','javdreams',
                     'bukkake','PornIsCheating','pornrelapsed',
                     'ClassyPornstars','ModelsGoneMild','AvaAddams',
                     'RileyReid','SavannahBond','tiktokthots','GirlsFinishingTheJob',
                     'GoonetteHub']

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



filename = 'to_upload.mp4'
subreddit = random.choice(list_of_subreddits)
for x in reddit.subreddit(subreddit).top(time_filter='day',limit=25):
    #print(subreddit)
    if 'redgifs' in x.url:
        url = x.url
        #print(url)
        #resp = requests.get(url) # making requests to server
        #with open(filename, "wb") as f: # opening a file handler to create new file 
        #    f.write(resp.content) # writing content to file
        red_gifs_api = redgifs.API()
        red_gifs_api.login()
        red_gifs_api.download(url, filename)
        
        tweet_title=x.title
        break

clip = VideoFileClip(filename)
duration = clip.duration
file_size = os.stat(filename).st_size
max_chunk_size = 5000000
seconds_per_chunk = duration/(file_size/max_chunk_size)
num_of_chunks = math.ceil(file_size/max_chunk_size)
final_file_size = seconds_per_chunk*num_of_chunks
print(duration, seconds_per_chunk, num_of_chunks, final_file_size)
lines = ''
for x in range(num_of_chunks):
    lines = lines + str(round(x*seconds_per_chunk,3)) + '-' + str(round((x+1)*seconds_per_chunk,3)) + '\n'

print(lines)
with open("times.txt", "w") as text_file:
    text_file.write(lines)

# Replace the filename below.
required_video_file = 'to_upload.mp4'

with open("times.txt") as f:
    times = f.readlines()

times = [x.strip() for x in times] 
dir_name = 'vid_chunks'
try:
    os.mkdir(dir_name)
except:
    pass
for time_ in times:
    starttime = float(time_.split("-")[0])
    endtime = float(time_.split("-")[1])
    ffmpeg_extract_subclip(required_video_file, starttime, endtime, targetname='vid_chunks/'+str(times.index(time_)+1)+".mp4")

video_parts = os.listdir('vid_chunks')
video_parts = list(set(['vid_chunks/'+x for x in video_parts]))
video_parts.sort(key=lambda x: os.path.getmtime(x))
print(video_parts)
#print(os.stat('vid_chunks/7.mp4'))
final_size = 0
part_size = os.stat(video_parts[0]).st_size 
for x in video_parts:
    final_size = final_size+os.stat(x).st_size 
    
print(final_size)
print(os.stat(video_parts[0]).st_size)

resp = twitter_api_authorized.upload_media_chunked_init(
    total_bytes=final_size,
    media_type="video/mp4",
)
media_id = resp.media_id_string

for idx, part in enumerate(video_parts):
    with open(part, "rb") as media:
        status = twitter_api_authorized.upload_media_chunked_append(
            media_id=media_id,
            media=media,
            segment_index=idx,
        )
        print(part, status)

resp = twitter_api_authorized.upload_media_chunked_finalize(media_id=media_id)
print(resp)


time.sleep(10)
resp = twitter_api_authorized.upload_media_chunked_status(media_id=media_id)
print(resp)

twitter_api_authorized.create_tweet(
    text=tweet_title,
    media_media_ids=[media_id],
)

os.remove(filename)
os.remove('times.txt')
shutil.rmtree(dir_name)

