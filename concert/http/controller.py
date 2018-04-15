import os 
import binascii
from flask import Flask, Response, Blueprint, request, url_for, render_template, redirect, url_for, current_app, session

from concert.http.loginmanager import ConcertLoginManager
from concert.dbconnector import MongoConnector

ConcertHTTPServer = Flask(__name__, static_url_path=os.getcwd() + "/static", template_folder=os.getcwd() + "/templates")
ConcertHTTPServer.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24))

from concert.http.routes import ConcertRESTRoutes
ConcertHTTPServer.register_blueprint(ConcertRESTRoutes)