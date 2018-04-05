import youtube_dl
import soundcloud
import pymongo
import pafy
import requests
import json
import shutil
import os
import logging
from pathlib import Path
from celery import Celery
from celery.utils.log import get_task_logger
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song
from config import config
from utils.logutils import configure_celery_logger

LOGS_PATH = 'logs'
REDIS_URL = 'redis://localhost:6379/1'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'
THUMBNAIL_PATH = 'static/thumbnails/'
JPG_EXTENSION = '.jpg'

# Celery Setup
CELERY_NAME = 'concert'
celery = Celery(CELERY_NAME, backend=REDIS_URL, broker=REDIS_URL)

# Flask SocketIO Reference
socketio = SocketIO(message_queue=REDIS_URL)

# Setup Logger
logger = get_task_logger('concert.celery')
configure_celery_logger(logger)

# Setup Soundcloud
SOUNDCLOUD_CLIENT_ID = config["SOUNDCLOUD_CLIENT_ID"]
sc_client = soundcloud.Client(client_id=SOUNDCLOUD_CLIENT_ID)

@celery.task
def async_download(url, user_name):
	client = MongoClient()
	db = client.concert

	if "youtube.com" in url:
		# Try to parse url as playlist otherwise treat it as single song
		try:
			playlist = pafy.get_playlist(url)
			videos = playlist["items"]
			for video in videos:
				try:
					song_dict = _get_yt_song(video["pafy"])
					_add_song_to_queue(song_dict, user_name, db)
				except Exception as e:
					logger.error('Invalid Youtube url', exc_info=True)
		except Exception as e:
			video = pafy.new(url)
			song_dict = _get_yt_song(video)
			_add_song_to_queue(song_dict, user_name, db)
	elif "soundcloud.com" in url:
		try:
			sc_object = sc_client.get('/resolve', url=url)
		except requests.exceptions.HTTPError:
			logger.warning('Soundcloud track unavailable')
			return
		if sc_object.fields()["kind"] == "playlist":
			playlist = sc_client.get('/playlists/' + str(sc_object.id))
			tracks = playlist.tracks
			for track in tracks:
				song_dict = _get_sc_song(track)
				_add_song_to_queue(song_dict, user_name, db)
		else:
			track = sc_client.get('/tracks/' + str(sc_object.id)).fields()
			song_dict = _get_sc_song(track)
			_add_song_to_queue(song_dict, user_name, db)
	
def _get_yt_song(video):
	s = {}
	# Get video information
	s["song_title"] = video.title
	s["song_id"] = video.videoid
	s["song_duration"] = video.length * 1000
	s["stream_url"] = video.audiostreams[0].url
	logger.info("Getting info for: {}".format(s["song_title"]))

	s["thumbnail_url_1"] = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s["song_id"], MAXRES_THUMBNAIL)
	s["thumbnail_url_2"] = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s["song_id"], MQ_THUMBNAIL)
	return s

def _get_sc_song(track):
	s = {}
	# Get song information
	s["stream_url"]= sc_client.get(track["stream_url"], allow_redirects=False).location
	s["song_title"] = track["title"]
	s["song_id"] = track["id"]
	s["song_duration"] = track["duration"]
	logger.info("Getting info for: {}".format(s["song_title"]))

	s["thumbnail_url_1"] = track["artwork_url"].replace('large', 't500x500')
	s["thumbnail_url_2"] = track["artwork_url"].replace('large', 'crop')
	return s

def _add_song_to_queue(sd, user_name, db):
	# Download Thumbnail
	logger.info("Downloading Thumnail")
	thumbnail_path = _download_thumbnail(sd["thumbnail_url_1"], sd["thumbnail_url_2"], str(sd["song_id"]))
	logger.info("Finished Downloading Thumbnail")

	# Tell client we've finished downloading
	new_song = Song(sd["stream_url"], sd["song_title"], sd["song_duration"], thumbnail_path, user_name)
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

def _download_thumbnail(primary_url, secondary_url, song_id):
	path = "{}{}{}".format(THUMBNAIL_PATH, song_id, JPG_EXTENSION)
	if os.path.isfile(path):
		logger.info("Reusing existing thumbnail image")
		return path

	r1 = requests.get(primary_url, stream=True)
	if r1.status_code == 200:
		with open(path, 'wb+') as f:
			r1.raw.decode_content = True
			shutil.copyfileobj(r1.raw, f)  
		return path

	r2 = requests.get(secondary_url, stream=True)
	if r2.status_code == 200:
		with open(path, 'wb+') as f:
			r2.raw.decode_content = True
			shutil.copyfileobj(r2.raw, f)  
		return path

	logger.warning("Could not download thumbnail image for: {}".format(url))
	return None  
