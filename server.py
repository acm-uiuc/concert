import binascii
import os
import validators
import sys
import downloader as dl
from flask import Flask, request, url_for, render_template
from flask_socketio import SocketIO, send, emit
from celery import Celery
from pymongo import MongoClient
from celery_tasks import async_download
from service import MusicService

app = Flask(__name__)
app.config['SECRET KEY'] = binascii.hexlify(os.urandom(24))
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

socketio = SocketIO(app)
ms = MusicService(socketio)
ms.start()

client = MongoClient()
db = client.concert

@socketio.on('connect')
def handle_connection():
	socketio.emit('connected', ms.player_state(), include_self=True)

@socketio.on('play')
def handle_play(url):
	ms.play_next()

@socketio.on('pause')
def handle_pause():
	socketio.emit('pause', ms.pause(), include_self=True)

@socketio.on('volume')
def handle_volume(newVolume):
	socketio.emit('volume', ms.set_volume(newVolume), include_self=True)

@socketio.on('skip')
def handle_skip():
	socketio.emit('skip', ms.play_next(), include_self=True)

@socketio.on('stop')
def handle_stop():
	socketio.emit('stop', ms.stop(), include_self=True)

@socketio.on('download')
def handle_download(url):
	if not validators.url(url):
		emit('download_error')

	async_download.apply_async(args=[url])
	socketio.emit('download', ms.player_state(), include_self=True)
	
@socketio.on('position')
def handle_position():
	percentage = float(request.values.get('percentage'))
	socketio.emit('position', ms.set_time(percentage), include_self=True) 

@app.route('/')
def index():
	return render_template("index.html")

if __name__ == '__main__':
	socketio.run(app, debug=True, use_reloader=False)