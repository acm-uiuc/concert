import binascii
import os
import validators
import sys
import requests
import functools
import flask_login
from flask import Flask, request, url_for, render_template, redirect, url_for, current_app, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send, emit, disconnect
from celery import Celery
from pymongo import MongoClient
from celery_tasks import async_download
from service import MusicService
from models import User
from config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24))
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app)
ms = MusicService(socketio)
ms.start()

client = MongoClient()
db = client.concert

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return False
        else:
            return f(*args, **kwargs)
    return wrapped

@login_manager.user_loader
def load_user(uid):
	res = User.get_by_id(db, uid)
	if res == None:
		return None
	newuser = User(res['uid'], res['first_name'], res['last_name'])
	return newuser

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
@authenticated_only
def handle_download(url):
	if not validators.url(url):
		emit('download_error')

	async_download.apply_async(args=[url])
	socketio.emit('download', ms.player_state(), include_self=True)
	
@socketio.on('position')
@authenticated_only
def handle_position():
	percentage = float(request.values.get('percentage'))
	socketio.emit('position', ms.set_time(percentage), include_self=True) 

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']

	headers = {
		'Authorization': config['GROOT_TOKEN'],
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	payload = {
		"username": username,
		"password": password,
		"validation-factors": {
			"validationFactors": [{
				"value": "127.0.0.1",
				"name": "remote_address"
			}]
		}
	}
	resp = requests.post('https://api.acm.illinois.edu/session', headers=headers, json=payload)
	if resp.status_code != 200:
		return 'Invalid User'

	data = resp.json()
	token = data['token']

	user_resp = requests.get('https://api.acm.illinois.edu/session/'+token, headers=headers)
	if user_resp.status_code != 200:
		return 'Invalid Session Token'

	user_data = user_resp.json()['user']
	cur_user = User(user_data['name'], user_data['first-name'], user_data['last-name'])
	db.Users.insert_one(cur_user.__dict__)

	#Register User Session
	val = login_user(cur_user)

	return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
	db.Users.delete_many({"uid": current_user.uid})
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
	socketio.run(app, debug=True, use_reloader=False)