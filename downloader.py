import youtube_dl
import pymongo
import pafy
import requests
import json
import shutil
import os
from pathlib import Path
from celery import Celery
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song

REDIS_URL = 'redis://localhost:6379/1'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
THUMBNAIL_PATH = 'static/thumbnails/'
JPG_EXTENSION = '.jpg'

# Celery Setup
CELERY_NAME = 'concert'
celery = Celery(CELERY_NAME, backend=REDIS_URL, broker=REDIS_URL)

# Flask SocketIO Reference
socketio = SocketIO(message_queue=REDIS_URL)

@celery.task
def async_download(url, user_name):
	client = MongoClient()
	db = client.concert
	# Try to parse url as playlist otherwise treat it as single song
	try:
		playlist = pafy.get_playlist(url)
		videos = playlist["items"]
		for video in videos:
			try:
				_add_song_to_queue(video["pafy"], user_name, db)
			except Exception as e:
				print('Invalid Song Url')
	except Exception as e:
		video = pafy.new(url)
		_add_song_to_queue(video, user_name, db)
	
def _add_song_to_queue(video, user_name, db):
	# Get video information
	song_title = video.title
	song_id = video.videoid
	song_duration = video.length * 1000
	stream_url = video.audiostreams[0].url
	print("Getting info for: " + song_title)

	# Download Thumbnail
	print("Downloading Thumnail")
	thumbnail_url = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, song_id, MAXRES_THUMBNAIL)
	thumbnail_path = _download_thumbnail(thumbnail_url, str(song_id))
	print("Finished Downloading Thumbnail")

	# Tell client we've finished downloading
	new_song = Song(stream_url, song_title, song_duration, thumbnail_path, user_name)
	db.Queue.insert_one(new_song.dictify())
	socketio.emit('queue_change', json.dumps(_get_queue(db)), include_self=True)

def _file_exists(mrl):
	file = Path(mrl)
	return file.is_file()

def _get_queue(db):
	queue = []
	mongo_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
	for item in mongo_queue:
		song = Song(item['mrl'], item['title'], item['duration'], 
			item['thumbnail'], item['playedby'])
		queue.append(song.dictify())
	return queue

def _download_thumbnail(url, song_id):
	path = "{}{}{}".format(THUMBNAIL_PATH, song_id, JPG_EXTENSION)
	# Reuse thumbnail if it already exists
	if os.path.isfile(path):
		return path

	r = requests.get(url, stream=True)
	if r.status_code == 200:
		with open(path, 'wb+') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)  
		return path
	return None      
	
if __name__ == '__main__':
    celery.start()
