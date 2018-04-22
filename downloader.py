import json
import shutil
import os
import logging
import traceback
import soundcloud
import spotipy
import pymongo
import pafy
import requests
from pathlib import Path
from celery import Celery
from celery.utils.log import get_task_logger
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from spotipy.oauth2 import SpotifyClientCredentials
from models import Song
from config import config
from utils.logutils import configure_celery_logger
from utils.songutils import get_spotify_playlist, yt_search, get_spotify_track

REDIS_URL = 'redis://localhost:6379/1'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'
THUMBNAIL_PATH = os.path.join('static', 'thumbnails/')
JPG_EXTENSION = '.jpg'
DEFAULT_THUMBNAIL = "https://i.ytimg.com/vi/gh_dFH-Waes/maxresdefault.jpg"

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
	elif "spotify.com" in url:
		playlist = get_spotify_playlist(url, "items(track(name,artists(name),album(name,images)))", True)
		spotify_tracks = [_parse_spotify_track(track["track"]) for track in playlist["items"]]
		for spotify_track in spotify_tracks:
			try:
				song_dict = _get_spotify_song(spotify_track)
				_add_song_to_queue(song_dict, user_name, db)
			except Exception as e:
				print(traceback.format_exc())
	elif "spotify:track" in url:
		uri_parts = url.split(':')
		track_id = uri_parts[2]
		sp_track = _parse_spotify_track(get_spotify_track(track_id))
		song_dict = _get_spotify_song(sp_track)
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

	try:
		s["thumbnail_url_1"] = track["artwork_url"].replace('large', 't500x500')
		s["thumbnail_url_2"] = track["artwork_url"].replace('large', 'crop')
	except:
		s["thumbnail_url_1"] = DEFAULT_THUMBNAIL
		s["thumbnail_url_2"] = DEFAULT_THUMBNAIL
	return s

def _get_spotify_song(spotify_track):
	# Get video information
	track_name = spotify_track["name"] + " - " + ', '.join(spotify_track["artists"])
	s = _get_yt_version(spotify_track, track_name)

	# Overwrite with Spotify Info
	s["song_title"] = track_name
	s["thumbnail_url_1"] = spotify_track["art"]
	s["thumbnail_url_2"] = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, s["song_id"], MAXRES_THUMBNAIL)
	return s

def _parse_spotify_track(sp_track):
	spotify_track = {}
	spotify_track["name"] = sp_track["name"]
	spotify_track["artists"] = [artist["name"] for artist in sp_track["artists"]]
	if len(sp_track["album"]["images"]) > 0:
		spotify_track["art"] = sp_track["album"]["images"][0]["url"]
	else:
		spotify_track["art"] = ""
	return spotify_track

def _get_yt_version(spotify_track, q):
	# Get the best YouTube match
	yt_track = yt_search(q, 1)[0]
	# Get Song Info from Pafy
	video_url = "https://www.youtube.com/watch?v=" + yt_track["id"]["videoId"]
	video = pafy.new(video_url)
	return _get_yt_song(video)

def _add_song_to_queue(sd, user_name, db):
	# Download Thumbnail
	logger.info("Downloading Thumnail")
	thumbnail_path = _download_thumbnail(sd["thumbnail_url_1"], sd["thumbnail_url_2"], str(sd["song_id"]))
	logger.info("Finished Downloading Thumbnail")

	# Tell client we've finished downloading
	new_song = Song(str(sd["song_id"]), sd["stream_url"], sd["song_title"], sd["song_duration"], thumbnail_path, user_name)
	db.Queue.insert_one(new_song.dictify())
	socketio.emit('queue_change', json.dumps(_get_queue(db)), include_self=True)

def _file_exists(mrl):
	file = Path(mrl)
	return file.is_file()

def _get_queue(db):
	queue = []
	cur_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
	for item in cur_queue:
		song = Song(item['mid'], item['mrl'], item['title'], item['duration'], 
			item['thumbnail'], item['playedby'])
		queue.append(song.dictify())
	return json.dumps(queue)

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
