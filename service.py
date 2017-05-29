from models import Song
from player import Player
import downloader as dl

import vlc
import time
import threading
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.concert

class MusicService:
	def __init__(self):
		self.player = Player()

	def play_next(self):
		cur_queue = self.get_queue()
		if len(cur_queue) > 0:
			next_song = cur_queue.pop(0)
			self.player.play(next_song['mrl'])
			self.player.current_track = next_song
			self._remove_song(next_song['_id'])
		else:
			self.player.stop()

	def get_queue(self):
		queue = []
		cur_queue = db.Queue.find().sort('date', pymongo.ASCENDING)
		for item in cur_queue:
			queue.append(item)
		return queue

	def _remove_song(self, _id):
		db.Queue.delete_one({"_id": ObjectId(_id)})

	def set_time(self, percent):
		if not self.player.is_playing():
			return "Invalid"
		self.player.set_time(percent)
		return "done"

	def player_thread(self):
		while True:
			if not self.player.is_playing():
				self.play_next()
			time.sleep(.20)

	def start(self):
		thread = threading.Thread(target=self.player_thread)
		thread.daemon = True
		thread.start()