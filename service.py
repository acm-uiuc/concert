import sys
import random
import json
import time
import threading
import logging
import vlc
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song
from player import Player

PLAY_NEXT_DELAY = 0.8
HEARTBEAT_DELAY = 60

# Get logger
logger = logging.getLogger('concert')

class MusicService:
    """This class acts as a service layer on top of the player to handle business logic

    Args:
        socketio (Flask_SocketIO object): socketio object to use in the service
        db (MongoDB reference): Mongo reference to use in the service

    Attributes:
        _player (Player): Player object to control
        socketio (Flask_SocketIO object): socketio instance to send messages through
        has_stopped (bool): Boolean representing whether or not the player has already stopped
        should_skip (bool): Boolean representing whether or not the current song should be skipped
        db (MongoDB referenece): Reference to the mongodb instance
    """
    def __init__(self, socketio, db):
        self._player = Player()
        self.socketio = socketio
        self.has_stopped = False
        self.should_skip = False
        self.db = db

    def skip(self):
        """Sets the should_skip flag"""
        self.should_skip = True

    def pause(self):
        """Toggles play/pause in our player"""
        return self._player.pause()

    def stop(self):
        """Stops the current song

        Returns:
            Dictionary of the current state of the player
        """
        self._player.stop()
        return self.player_state()

    def set_volume(self, value):
        """"Sets the volume of the player

        Args:
            value (int): New volume value
        Returns:
            Returns a json string containing the new volume
        """
        return self._player.set_volume(value)

    def clear_queue(self):
        """Clears the current queue

        Returns:
            json string containing an empty queue
        """
        self.db.Queue.delete_many({})
        return self._get_json_queue()

    def remove_song(self, song_id):
        """Removes a song with the given id off the queue
        
        Args:
            song_id (str): Song id to remove

        Returns:
            json string containing the current queue
        """
        self.db.Queue.delete_one({"id": song_id})
        return self._get_json_queue()

    def player_state(self):
        """Gets the current player state and combines it with the queue

        Returns:
            json string containing the player state and queue
        """
        player_state = json.loads(self._player.cur_state())
        player_state['queue'] = self._get_json_queue()
        return json.dumps(player_state)

    def _get_next_song(self):
        """Gets the next song from the queue stored in Mongo

        Returns:
            The song at the top of the queue
        """
        first_item = self.db.Queue.find().sort('date', pymongo.ASCENDING).limit(1)
        return first_item[0]

    def _get_queue_size(self):
        """Returns the current size of the queue"""
        return self.db.Queue.count()

    def _get_json_queue(self):
        """Gets the current queue

        Returns:
            The current queue in json form
        """
        queue = []
        cur_queue = self.db.Queue.find().sort('date', pymongo.ASCENDING)
        for item in cur_queue:
            song = Song(item['id'], item['stream'], item['title'], item['duration'], 
                item['thumbnail'], item['playedby'])
            queue.append(song.dictify())
        return json.dumps(queue)

    def _remove_song_from_queue(self, _id):
        """Removes a song on the queue with the given id

        Args:
            _id (string): Mongo id of the song to remove
        """
        self.db.Queue.update({"_id": ObjectId(_id)})

    def _player_thread(self):
        """Thread that controls music playing

        Checks to see if the player is currently playing a song.
        If not, it will attempt to pull from the top of the queue.
        Otherwise it'll continue on until the next iteration
        """
        while True:
            if not self._player.is_playing() or self.should_skip:
                self.should_skip = False
                self._play_next()
            time.sleep(PLAY_NEXT_DELAY)

    def _heartbeat(self):
        """Heartbeat thread to broadcast to clients every 1 minute"""
        while True:
            self.socketio.emit('heartbeat', self.player_state(), include_self=True)
            time.sleep(HEARTBEAT_DELAY)

    def _play_next(self):
        """Plays the next song on the queue

        Checks to see if the queue has songs in it. If the queue does,
        this function will pop the first song and play it
        """
        if self._get_queue_size() > 0:
            logger.info("Playing next song")
            next_song = self._get_next_song()
            self._player.current_track = next_song
            self._remove_song_from_queue(next_song['_id'])
            self._player.play(next_song)
            self.socketio.emit('played', self.player_state(), include_self=True)
            self.has_stopped = False
        else:
            # We need to emit a signal to stop clients, but this should only occur once while
            # there is no media in the player
            if not self.has_stopped:
                self._player.stop()
                self.socketio.emit('stopped', self.player_state(), include_self=True)
                self.has_stopped = True
                logger.info("Player is stopped")

    def start(self):
        """Function to start up the player and heartbeat threads"""
        player_thread = threading.Thread(target=self._player_thread)
        player_thread.daemon = True
        player_thread.start()

        heartbeat_thread = threading.Thread(target=self._heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
