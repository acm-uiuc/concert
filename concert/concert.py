import os
import binascii
from flask import Flask, Response, Blueprint, request, url_for, render_template, redirect, url_for, current_app, session

from concert.service import ConcertService
from concert.http.controller import ConcertHTTPServer
from concert.http.loginmanager import ConcertLoginManager
from concert.http.routes import ConcertRESTRoutes
from concert.http.events import ConcertEventsSockets, ConcertRedisClient, handlers, notifiers

ConcertServiceInstance = ConcertService()


def start_concert(config):
    ConcertHTTPServer.config["GROOT_TOKEN"] = config["http"]["groot_token"]
    ConcertHTTPServer.config["authentication"] = config["http"]["authentication"]
    ConcertHTTPServer.config["dev_user"] = config["http"]["dev_user"]
    handlers.register_handlers()

    ConcertLoginManager.init_app(ConcertHTTPServer)
    ConcertEventsSockets.init_app(ConcertHTTPServer, async_mode='gevent', async_handlers=True)
    ConcertRedisClient.init_app(ConcertHTTPServer)
    ConcertServiceInstance.init_app(config["service"])

    ConcertEventsSockets.run(ConcertHTTPServer, debug=config["debug"], use_reloader=config["debug"], log_output=config["debug"], host='0.0.0.0')

def get_service():
    return ConcertServiceInstance
