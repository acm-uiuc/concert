import hashlib
import time
import json

class ConcertQueue():
    def __init__(self):
        self.queue = []

    def add_to_queue(self, music, prepend=False):
        if type(music) is list:
            for song in music:
                song["id"] = self.generate_track_id(song)
                print("------QUEUEING------")
                print("Title: %s" % song['title'])
                print("ID: %s" % song["id"])
                print("------QUEUEING------")
                if prepend:
                    self.queue.insert(0, song)
                else:
                    self.queue.append(song)
        elif type(music) is dict:
            music["id"] = self.generate_track_id(music)
            print("------QUEUEING------")
            print("Title: %s" % music['title'])
            print("------QUEUEING------")
            if prepend:
                self.queue.insert(0, music)
            else:
                self.queue.append(music)

    def remove_song_from_queue(self, track_id):
        for i in range(len(self.queue)):
            if self.queue[i]["id"] == track_id:
                self.queue.pop(i)
                print(self.queue)
                return

    def requeue_song(self, old_id, new_id):
        print("------REQUEUEING------")
        print("Old Position: %s New Position: %s" % (old_id, new_id))
        self.queue.insert(int(new_id), self.queue.pop(int(old_id)))

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
