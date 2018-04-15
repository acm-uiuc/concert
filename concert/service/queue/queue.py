import json

class ConcertQueue():
    def __init__(self):
        self.queue = []

    def add_to_queue(self, music):
        if type(music) is list:
            for song in music:
                self.queue.append(song)
        elif type(music) is dict:
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
        return self.queue.pop()

    def clear_queue(self):
        self.queue = []