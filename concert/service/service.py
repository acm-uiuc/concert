import time
import threading
import sys
import random
import json
from copy import deepcopy

from concert.models import Song
from concert.thridparty import vlc
from concert.service.player import ConcertPlayer
from concert.service.queue import ConcertQueue
from concert.http.events import notifiers
from concert.service.fetchers import YoutubeFetcher, SoundcloudFetcher
from concert.service.searchers import YoutubeSearcher, SoundcloudSearcher


class ConcertService:
    state = {
        "has_stopped": False,
        "should_skip": False
    }

    def __init__(self):
        self.queue = ConcertQueue()

    def init_app(self, config):
        self.youtube_fetcher = YoutubeFetcher(config["providers"]["youtube"])
        self.soundcloud_fetcher = SoundcloudFetcher(config["providers"]["soundcloud"])
        self.youtube_searcher = YoutubeSearcher(config["providers"]["youtube"])
        self.soundcloud_searcher = SoundcloudSearcher(config["providers"]["soundcloud"]) 

        self.player = ConcertPlayer(config["player"])

        self.PLAYER_UPDATE_INTERVAL = config["player_update_interval"]
        self.HEARTBEAT_DELAY = config["heartbeat_delay"]

        player_thread = threading.Thread(target=self.player_thread)
        player_thread.daemon = True
        player_thread.start()

        heartbeat_thread = threading.Thread(target=self.heartbeat_thread)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    def player_thread(self):
        while True:
            if not self.player.is_playing() or self.state["should_skip"]:
                self.state["should_skip"] = False
                self.play_next()
            time.sleep(self.PLAYER_UPDATE_INTERVAL)

    def heartbeat_thread(self):
        while True:
            notifiers.notify_heartbeat(self.service_state())
            time.sleep(self.HEARTBEAT_DELAY)

    def search(self, query, part, max_length, timeout):
        ''' Need to figure out rate limiting for youtube'''
        return self.soundcloud_searcher.search(query, part, max_length)# + self.youtube_searcher.search(query, part, max_length)

    def queue_new_song(self, song_url, user):
        song_info_list = None
        if "youtube.com" in song_url:
            song_info_list = self.youtube_fetcher.fetch_song(song_url)
        elif "soundcloud.com" in song_url:
            song_info_list = self.soundcloud_fetcher.fetch_song(song_url)
        else:
            # CHANGE TO FAILED TO 
            return notifiers.notify_failed_queue(self.service_state())

        for song in song_info_list: 
            song["playedby"] = user

        print(song_info_list)
        self.queue.add_to_queue(song_info_list)

        #notifiers.notify_song_queue(self.service_state())
        notifiers.notify_queue_change(self.service_state())

    def clear_queue(self):
        self.queue.clear_queue()
        notifiers.notify_queue_change(self.service_state())
        #notifiers.notify_clear_queue(self.service_state())

    def play_next(self):
        queue_size = self.queue.get_queue_size()
        if queue_size > 0:
            next_song = self.queue.get_next_song()
            self.player.current_track = next_song
            print(next_song)
            
            self.player.play(next_song)

            notifiers.notify_new_song_playing(self.service_state())

            self.state["has_stopped"] = False
        else:
            # We need to emit a signal to stop clients, but this should only occur once while
            # there is no media in the player
            if (not self.state["has_stopped"]):
                self.player.stop()

                notifiers.notify_no_song_playing(self.service_state())

                self.state["has_stopped"] = True

    def skip(self):
        self.state["should_skip"] = True
        notifiers.notify_song_skip(self.service_state())

    def pause(self):
        self.player.pause()
        notifiers.notify_paused(self.service_state())


    def stop(self):
        self.player.stop()
        notifiers.notify_paused(self.player.player_state())

    def set_volume(self, value):
        self.player.set_volume(value)
        notifiers.notify_volume_change({"volume": self.player.volume})


    def set_time(self, percent):
        if not self.player.is_playing():
            notifiers.notify_failed_to_set_time({"error": "invalid"})
        
        self.player.set_time(percent)
        notifiers.notify_set_time(self.service_state())

    # Combine the player's state with the current queue
    def service_state(self):
        # Remove track url to prevent leaking client_id
        player_state = deepcopy(self.player.player_state())
        if "track_url" in player_state:
            del player_state['track_url']
        queue_state = deepcopy(self.queue.get_queue())
        for q in queue_state:
            if "track_url" in q:
                del q["track_url"]
        return {
            "player": player_state,
            "queue": queue_state
        }
