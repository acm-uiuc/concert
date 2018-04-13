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
    def __init__(self, socketio, db):
        self._player = Player()
        self.socketio = socketio
        self.has_stopped = False
        self.should_skip = False
        self.db = db

    def skip(self):
        self.should_skip = True

    def pause(self):
        return self._player.pause()

    def stop(self):
        self._player.stop()
        return self.player_state()

    def set_volume(self, value):
        return self._player.set_volume(value)

    def clear_queue(self):
        self.db.Queue.delete_many({})
        return self._get_json_queue()

    def remove_song(self, song_id):
        print(song_id)
        self.db.Queue.delete_one({"mid": song_id})
        return self._get_json_queue()

    # Combine the player's state with the current queue
    def player_state(self):
        player_state = json.loads(self._player.cur_state())
        player_state['queue'] = self._get_json_queue()
        return json.dumps(player_state)

    def _get_next_song(self):
        first_item = self.db.Queue.find().sort('date', pymongo.ASCENDING).limit(1)
        return first_item[0]

    def _get_queue_size(self):
        return self.db.Queue.count()

    def _get_json_queue(self):
        queue = []
        cur_queue = self.db.Queue.find().sort('date', pymongo.ASCENDING)
        for item in cur_queue:
            song = Song(item['mid'], item['mrl'], item['title'], item['duration'], 
                item['thumbnail'], item['playedby'])
            queue.append(song.dictify())
        return json.dumps(queue)

    def _remove_song_from_queue(self, _id):
        self.db.Queue.delete_one({"_id": ObjectId(_id)})

    def _player_thread(self):
        while True:
            if not self._player.is_playing() or self.should_skip:
                self.should_skip = False
                self._play_next()
            time.sleep(PLAY_NEXT_DELAY)

    def _heartbeat(self):
        while True:
            self.socketio.emit('heartbeat', self.player_state(), include_self=True)
            time.sleep(HEARTBEAT_DELAY)

    def _play_next(self):
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
        player_thread = threading.Thread(target=self._player_thread)
        player_thread.daemon = True
        player_thread.start()

        heartbeat_thread = threading.Thread(target=self._heartbeat)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
