import binascii
import os
from flask import Flask, request, url_for, render_template
from flask_socketio import SocketIO, send, emit
from flask_celery import make_celery
from celery_tasks import async_download
from service import MusicService
from celery import Celery
from pymongo import MongoClient
import validators
import sys
import downloader as dl

app = Flask(__name__)
app.debug = True
app.config['SECRET KEY'] = binascii.hexlify(os.urandom(24))
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

celery = make_celery(app)
socketio = SocketIO(app)

ms = MusicService(socketio)
ms.start()

client = MongoClient()
db = client.concert

@socketio.on('connect')
def handle_connection():
	socketio.emit('connected', ms.player.cur_state(), include_self=True)

@socketio.on('play')
def handle_play(url):
	#socketio.emit('play', ms.player.play(url), include_self=True)
	ms.play_next()

@socketio.on('pause')
def handle_pause():
	socketio.emit('pause', ms.player.pause(), include_self=True)

@socketio.on('volume')
def handle_volume(newVolume):
	socketio.emit('volume', ms.player.set_volume(newVolume), include_self=True)

@socketio.on('skip')
def handle_skip():
	socketio.emit('skip', ms.play_next(), include_self=True)

@socketio.on('stop')
def handle_stop():
	socketio.emit('stop', ms.player.stop(), include_self=True)

@socketio.on('download')
def handle_download(url):
	if not validators.url(url):
		emit('download_error')

	downloaded_songs = db.Downloaded
	queried_song = downloaded_songs.find_one({'url': url})
	if queried_song != None:
		db.Queue.insert_one(queried_song)
		if(not ms.player.is_playing()):
			ms.play_next()
	else:
		async_download.apply_async(args=[url])
		socketio.emit('download', ms.player.cur_state(), include_self=True)
	

@socketio.on('position')
def handle_position():
	percentage = float(request.values.get('percentage'))
	socketio.emit('position', ms.set_time(percentage), include_self=True) 

@app.route('/')
def index():
	return render_template("index.html")

if __name__ == '__main__':
	socketio.run(app)