import requests
import datetime
import random


import requests, traceback, json, io, os, urllib.request, sys
#sys.stdout.reconfigure(encoding='utf-8')


def get_redgifs_embedded_video_url(redgifs_url, output_fn):
	API_URL_REDGIFS = 'https://api.redgifs.com/v2/gifs/'
	r = requests.get('https://api.redgifs.com/v2/auth/temporary')
	token = r.json()['token']

	headers={"Authorization": "Bearer "+token}
	try:
		print("redgifs_url = {}".format(redgifs_url))

		#Get RedGifs video ID
		redgifs_ID = redgifs_url.split('/watch/', 1)
		redgifs_ID = redgifs_ID[1]
		print("redgifs_ID = {}".format(redgifs_ID))
		
		sess = requests.Session()
		
		#Get RedGifs Video Meta
		# request = requests.get(API_URL_REDGIFS + redgifs_ID)
		request = sess.get(API_URL_REDGIFS + redgifs_ID, headers=headers)
		print(request)
		
		if request is None:
			return
		else:
			rawData = request.json()
			#print(rawData)
			#print("rawData = {}".format(rawData))

			#Get HD video url
			hd_video_url = rawData['gif']['urls']['hd']
			#print("hd_video_url = {}".format(hd_video_url))
			
			with sess.get(hd_video_url, stream=True) as r:
				with open(output_fn, 'wb') as f:
					for chunk in r.iter_content(chunk_size=8192): 
						# If you have chunk encoded response uncomment 
						# if and set chunk_size parameter to None.
						# if chunk: 
						f.write(chunk)

			return hd_video_url
	except Exception:
		traceback.print_exc()
		return
def convert_hastag_to_at(tweet_title_):
	if '#AngelWicky' in   tweet_title_:
		return  tweet_title_.replace('#AngelWicky','@Angel_Wicky_II')
	else:
		return tweet_title_

