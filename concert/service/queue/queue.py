import hashlib
import time
import json

class ConcertQueue():
    def __init__(self):
        self.queue = []

    def add_to_queue(self, music):
        if type(music) is list:
            for song in music:
                song["id"] = self.generate_track_id(song)
                print("------QUEUEING------")
                print("Title: %s" % song['title'])
                print("ID: %s" % song["id"])
                print("------QUEUEING------")
                self.queue.append(song)
        elif type(music) is dict:
            music["id"] = self.generate_track_id(music)
            print("------QUEUEING------")
            print("Title: %s" % music['title'])
            print("------QUEUEING------")
            self.queue.append(music)

    def remove_song_from_queue(self, track_id):
        pass

    def remove_last_song_from_queue(self):
        self.queue.pop()

    def get_queue(self):
        return self.queue

    def get_queue_size(self):
        return len(self.queue)

    def get_next_song(self):
        return self.queue.pop(0)

    def clear_queue(self):
        self.queue = []

    def generate_track_id(self, track):
        hash = hashlib.sha1()
        hash.update((str(time.time()) + track["title"]).encode('utf-8'))
        return hash.hexdigest()[:10]
