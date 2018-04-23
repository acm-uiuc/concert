import json
import shutil
import os
import logging
import traceback
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
from utils.youtube import search_yt_video, get_yt_audio
from utils.soundcloud import get_sc_object, get_sc_playlist, get_sc_track
from utils.spotify import get_sp_playlist, get_sp_track, extract_sp_track_info

REDIS_URL = 'redis://localhost:6379/1'

# Celery Setup
CELERY_NAME = 'concert'
celery = Celery(CELERY_NAME, backend=REDIS_URL, broker=REDIS_URL)

# Flask SocketIO Reference
socketio = SocketIO(message_queue=REDIS_URL)

# Setup Logger
logger = get_task_logger('concert.celery')
configure_celery_logger(logger)

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
					song = Song.from_yt_video(video["pafy"], user_name)
					_add_song_to_queue(song, db)
				except Exception as e:
					logger.error('Invalid Youtube url', exc_info=True)
		except Exception as e:
			video = pafy.new(url)
			song = Song.from_yt_video(video, user_name)
			_add_song_to_queue(song, db)
	elif "soundcloud.com" in url:
		try:
			sc_object = get_sc_object(url)
		except requests.exceptions.HTTPError:
			logger.warning('Soundcloud track unavailable')
			return
		if sc_object.fields()["kind"] == "playlist":
			playlist = get_sc_playlist(sc_object.id)
			for track in playlist:
				song = Song.from_sc_track(track, user_name)
				_add_song_to_queue(song, db)
		else:
			track = get_sc_track(sc_object.id)
			song = Song.from_sc_track(track, user_name)
			_add_song_to_queue(song, db)
	elif "spotify.com" in url:
		playlist = get_sp_playlist(url, "items(track(name,artists(name),album(name,images)))", True)
		sp_tracks = [extract_sp_track_info(track["track"]) for track in playlist["items"]]
		for sp_track in sp_tracks:
			try:
				yt_audio = get_yt_audio(sp_track)
				song = Song.from_sp_track(sp_track, yt_audio, user_name)
				_add_song_to_queue(song, db)
			except Exception as e:
				print(traceback.format_exc())
	elif "spotify:track" in url:
		uri_parts = url.split(':')
		track_id = uri_parts[2]
		sp_track = extract_sp_track_info(get_sp_track(track_id))
		yt_audio = get_yt_audio(sp_track)
		song = Song.from_sp_track(sp_track, yt_audio, user_name)
		_add_song_to_queue(song, db)

def _add_song_to_queue(song, db):
	# Tell client we've finished downloading
	db.Queue.insert_one(song.dictify())
	socketio.emit('queue_change', json.dumps(_get_queue(db)), include_self=True)

def _get_queue(db):
	queue = []
	cur_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
	for item in cur_queue:
		song = Song(item['id'], item['stream'], item['title'], item['duration'], 
			item['thumbnail'], item['playedby'])
		queue.append(song.dictify())
	return json.dumps(queue)
