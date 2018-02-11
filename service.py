import vlc
import time
import threading
import pymongo
import sys
import random
from pymongo import MongoClient
from bson.objectid import ObjectId
from models import Song
from player import Player

client = MongoClient()
db = client.concert

class MusicService:
	def __init__(self, socketio):
		self._player = Player()
		self.socketio = socketio

	def play_next(self):
		cur_queue = self.get_queue()
		if len(cur_queue) > 0:
			next_song = cur_queue.pop(0)
			self._player.current_track = next_song
			self._remove_song(next_song['_id'])
			self.socketio.emit('play', self._player.play(next_song), include_self=True)
		else:
			self._player.stop()
			return self._player.cur_state()

	def pause(self):
		return self._player.pause()

	def stop(self):
		return self._player.stop()

	def player_state(self):
		return self._player.cur_state()

	def set_volume(self, value):
		return self._player.set_volume(value)

	def set_time(self, percent):
		if not self._player.is_playing():
			return "Invalid"
		return self._player.set_time(percent)

	def get_queue(self):
		queue = []
		cur_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
		for item in cur_queue:
			queue.append(item)
		return queue

	def _remove_song(self, _id):
		db.Queue.delete_one({"_id": ObjectId(_id)})

	def player_thread(self):
		while True:
			if not self._player.is_playing():
				self.play_next()
			time.sleep(.20)

	def start(self):
		thread = threading.Thread(target=self.player_thread)
		thread.daemon = True
		thread.start()