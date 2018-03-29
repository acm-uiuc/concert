import binascii
import os
import validators
import sys
import requests
import functools
import flask_login
from flask import Flask, Response, request, url_for, render_template, redirect, url_for, current_app, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send, emit, disconnect
from pymongo import MongoClient
from downloader import async_download
from service import MusicService
from models import User
from config import config

app = Flask(__name__)
app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24))
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Flask-SocketIO
socketio = SocketIO(app, message_queue='redis://localhost:6379/1')
ms = MusicService(socketio)
ms.start()

# Pymongo
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


@socketio.on('pause')
@authenticated_only
def handle_pause():
    socketio.emit('paused', ms.pause(), include_self=True)


@socketio.on('volume')
@authenticated_only
def handle_volume(newVolume):
    socketio.emit('volume_changed', ms.set_volume(newVolume), include_self=True)


@socketio.on('skip')
@authenticated_only
def handle_skip():
    socketio.emit('skipped', ms.skip(), include_self=True)


@socketio.on('stop')
@authenticated_only
def handle_stop():
    socketio.emit('stopped', ms.stop(), include_self=True)


@socketio.on('download')
@authenticated_only
def handle_download(url):
    if not validators.url(url):
        emit('download_error')

    user_name = current_user.first_name + " " + current_user.last_name
    async_download.apply_async(args=[url, user_name])
    socketio.emit('downloaded', ms.player_state(), include_self=True)

@socketio.on('clear')
@authenticated_only
def clear_queue():
    socketio.emit('cleared', ms.clear_queue(), include_self=True)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

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
        return Response("Invalid Username/Password", status=400)

    data = resp.json()
    token = data['token']

    user_resp = requests.get('https://api.acm.illinois.edu/session/' + token, headers=headers)
    if user_resp.status_code != 200:
        return Response("Invalid Session Token", status=400)

    user_data = user_resp.json()['user']
    cur_user = User(user_data['name'], user_data['first-name'], user_data['last-name'])
    db.Users.insert_one(cur_user.__dict__)

    # Register User Session
    val = login_user(cur_user, remember=True)

    return Response("Success", 200);


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    print("Logging Out")
    db.Users.delete_many({"uid": current_user.uid})
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Clear users before starting up 
    db.Users.delete_many({})
    if not os.path.exists("static/thumbnails"):
        os.mkdir("static/thumbnails")
    socketio.run(app, debug=False, use_reloader=False, host='0.0.0.0')
