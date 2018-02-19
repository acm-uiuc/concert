import youtube_dl
import pymongo
import json
from celery import Celery
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song
from pathlib import Path

CELERY_NAME = 'concert'
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

celery = Celery(CELERY_NAME, backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'music/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    "extractaudio": True,
    "noplaylist": False
}
ytdl = youtube_dl.YoutubeDL(ydl_opts)
socketio = SocketIO(message_queue='redis://localhost:6379/1')

@celery.task
def async_download(url):
	client = MongoClient()
	db = client.concert

	info = ytdl.extract_info(url, download=False)
	if '_type' in info and info['_type'] == 'playlist':
		# Handle Playlist
		for entry in info['entries']:
			queried_song = db.Downloaded.find_one({'url': entry['webpage_url']})
			if queried_song != None:
				if _file_exists(queried_song['mrl']):
					new_song = Song(queried_song['mrl'], queried_song['title'], queried_song['url'], queried_song['duration'])
					db.Queue.insert_one(new_song.dictify())
					continue
				else:
					db.Downloaded.delete_one({'_id': ObjectId(queried_song['_id'])})

			info = ytdl.extract_info(entry['webpage_url'], download=True)
			song_id = info["id"]
			song_title = info["title"]
			song_duration = info["duration"] * 1000

			# This is jank for now
			song_mrl = "music/" + str(song_id) + ".mp3"
			new_song = Song(song_mrl, song_title, info['webpage_url'], song_duration)
			db.Queue.insert_one(new_song.dictify())
			db.Downloaded.insert_one(new_song.dictify())
	else:
		# If not a playlist assume single song
		queried_song = db.Downloaded.find_one({'url': url})
		if queried_song != None:
			if _file_exists(queried_song['mrl']):
				new_song = Song(queried_song['mrl'], queried_song['title'], queried_song['url'], queried_song['duration'])
				db.Queue.insert_one(new_song.dictify())
				socketio.emit('queue_change', json.dumps(_get_queue()), include_self=True)
				return
			else:
				db.Downloaded.delete_one({'_id': ObjectId(queried_song['_id'])})

		info = ytdl.extract_info(url, download=True)
		song_id = info["id"]
		song_title = info["title"]
		song_duration = info["duration"] * 1000

		# This is jank for now
		song_mrl = "music/" + str(song_id) + ".mp3"
		new_song = Song(song_mrl, song_title, url, song_duration)
		db.Queue.insert_one(new_song.dictify())
		db.Downloaded.insert_one(new_song.dictify())
		socketio.emit('queue_change', json.dumps(_get_queue()), include_self=True)

def _file_exists(mrl):
	file = Path(mrl)
	return file.is_file()

def _get_queue():
	client = MongoClient()
	db = client.concert
	queue = []
	cur_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
	for item in cur_queue:
		song = Song(item['mrl'], item['title'], item['url'], item['duration'])
		queue.append(song.dictify())
	return queue
	
if __name__ == '__main__':
    celery.start()
