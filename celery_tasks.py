import youtube_dl
from models import Song
from celery import Celery
from pymongo import MongoClient

import downloader as dl

CELERY_NAME = 'concert'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

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

@celery.task
def async_download(url):
	client = MongoClient()
	db = client.concert
	#Hopefully some front end validation done for urls
	info = ytdl.extract_info(url, download=True)

	song_id = info["id"]
	song_title = info["title"]

	#This is jank for now
	song_mrl = "music/" + str(song_id) + ".mp3"

	new_song = Song(song_mrl, song_title, url)
	db.Queue.insert_one(new_song.dictify())
	db.Downloaded.insert_one(new_song.dictify())
	
if __name__ == '__main__':
    celery.start()
