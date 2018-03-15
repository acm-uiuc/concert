import youtube_dl
import pymongo
import json
import requests
import shutil
from celery import Celery
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song
from pathlib import Path
import pafy

CELERY_NAME = 'concert'
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
celery = Celery(CELERY_NAME, backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)

ydl_opts = {
    'format': 'best',
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
def async_download(url, user_name):
	client = MongoClient()
	db = client.concert

	try:
		playlist = pafy.get_playlist(url)
		videos = playlist["items"]
		for video in videos:
			add_song_to_queue(video["pafy"], user_name, db)
	except Exception as e:
		video = pafy.new(url)
		add_song_to_queue(video, user_name, db)
	
def add_song_to_queue(video, user_name, db):
	# Get video information
	song_title = video.title
	song_id = video.videoid
	song_duration = video.length * 1000
	stream_url = video.audiostreams[0].url
	print("Getting info for: " + song_title)

	# Download Thumbnail
	print("Downloading Thumnail")
	thumbnail_url = 'https://img.youtube.com/vi/' + song_id + '/hqdefault.jpg'
	thumbnail_path = _download_thumbnail(thumbnail_url, str(song_id))
	print("Finished Downloading Thumbnail")

	# Tell client we've finished downloading
	new_song = Song(stream_url, song_title, song_duration, thumbnail_path, user_name)
	db.Queue.insert_one(new_song.dictify())
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
		song = Song(item['mrl'], item['title'], item['duration'], 
			item['thumbnail'], item['playedby'])
		queue.append(song.dictify())
	return queue

def _download_thumbnail(url, song_id):
	r = requests.get(url, stream=True)
	if r.status_code == 200:
		path = "static/thumbnails/" + song_id + ".jpg"
		with open(path, 'wb+') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)  
		return path
	return ""      
	
if __name__ == '__main__':
    celery.start()
