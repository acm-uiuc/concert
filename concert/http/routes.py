import os
import json
import requests
from flask import Flask, Response, Blueprint, request, url_for, send_from_directory, render_template, redirect, url_for, current_app, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

import concert
from concert.models import User
from concert.http.loginmanager import ConcertDBConnector
from concert.http.controller import ConcertHTTPServer

# Flask-Login
ConcertRESTRoutes = Blueprint('ConcertRESTRoutes', __name__)

@ConcertRESTRoutes.route('/')
def index():
    return render_template("index.html")

@ConcertRESTRoutes.route('/apple-app-site-association')
def apple():
    return send_static_file(os.getcwd() + "/static/ios-config", "apple-app-site-association")

@ConcertRESTRoutes.route('/static/<path:path>')
def serve_static_files(path):
    return send_from_directory(os.getcwd() + "/static", path)

@ConcertRESTRoutes.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    headers = {
        'Authorization': ConcertHTTPServer.config["GROOT_TOKEN"],
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
    
    ConcertDBConnector.add_user_session(cur_user)

    # Register User Session
    val = login_user(cur_user, remember=True)

    if val:
        return Response("Success", 200)
    else:
        return Response("Login Failed", 401)

@ConcertRESTRoutes.route("/logout", methods=['POST'])
@login_required
def logout():
    print("Logging Out")
    ConcertDBConnector.remove_user_session(current_user)
    logout_user()
    return redirect(url_for('index'))


@ConcertRESTRoutes.route('/search', methods=['GET'])
def search():
    q = request.args.get('q')
    part = request.args.get('part')
    max_results = request.args.get('maxResults')
    timeout = request.args.get('timeout')

    return json.dumps({"items": concert.get_service().search(q, part, max_results, timeout)})
