import os
import validators
from flask_login import current_user

import concert
from concert.http.events import ConcertEventsSockets, notifiers
from concert.http.controller import ConcertHTTPServer
from concert.http.loginmanager import authenticated_only

def register_handlers():
    @ConcertEventsSockets.on_error_default        # Handles the default namespace
    def error_handler(e):
        print(e)

    @ConcertEventsSockets.on('message')
    def handle_msg():
        print("HANDLER: CONNECTED TO CLIENT")
        

    @ConcertEventsSockets.on('c_connected')
    def handle_connection():
        print("HANDLER: CONNECTED TO CLIENT")
        state = concert.get_service().service_state()
        notifiers.notify_connected(state)

    @ConcertEventsSockets.on('c_pause')
    @authenticated_only
    def handle_pause():
        concert.get_service().pause()


    @ConcertEventsSockets.on('c_volume')
    @authenticated_only
    def handle_volume(newVolume):
        concert.get_service().set_volume(newVolume)


    @ConcertEventsSockets.on('c_skip')
    @authenticated_only
    def handle_skip():
        print("HANDLER: SKIP REQUESTED")
        concert.get_service().skip()


    @ConcertEventsSockets.on('c_stop')
    @authenticated_only
    def handle_stop():
        concert.get_service().stop()
        

    @ConcertEventsSockets.on('c_queue_song')
    @authenticated_only
    def handle_queue_song(url):
        if not validators.url(url):
            notifiers.notify_failed_queue({'err': 'invalid url'})
        user_name = current_user.first_name + " " + current_user.last_name
        concert.get_service().queue_new_song(url, user_name)

    @ConcertEventsSockets.on('c_clear')
    @authenticated_only
    def handle_queue_clearing():
        concert.get_service().clear_queue()