import time
import threading
import sys
import random
import json
from urllib.request import urlretrieve
import os
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
        "playing": False,
        "should_skip": False
    }

    def __init__(self):
        self.queue = ConcertQueue()
        self.artwork_download_queue = []
        self.artwork_delete_queue = []

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

        downloader_thread = threading.Thread(target=self.artwork_downloader_thread)
        downloader_thread.daemon = True
        downloader_thread.start()

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


    '''
    SEARCH
    '''
    def search(self, query, part, max_length, timeout):
        ''' Need to figure out rate limiting for youtube'''
        return self.youtube_searcher.search(query, part, max_length) + self.soundcloud_searcher.search(query, part, max_length)

    
    '''
    QUEUE MANAGEMENT
    '''

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

        notifiers.notify_queue_change(self.service_state())

    def remove_song(self, id):
        self.queue.remove_song_from_queue(id)
        notifiers.notify_queue_change(self.service_state())

    def requeue_song(self, old, new):
        self.queue.requeue_song(old, new)
        notifiers.notify_queue_change(self.service_state())

    def clear_queue(self):
        self.queue.clear_queue()
        notifiers.notify_queue_change(self.service_state())

    def play_next(self):
        queue_size = self.queue.get_queue_size()
        if queue_size > 0:
            if self.player.current_track != None:
                self.artwork_delete_queue.append(os.getcwd() + self.player.current_track["thumbnail_url"]) 
            next_song = self.queue.get_next_song()
            self.player.current_track = next_song
            self.get_artwork(next_song)
            self.player.current_track["thumbnail_url_src"] = self.player.current_track["thumbnail_url"] 
            self.player.current_track["thumbnail_url"] = "/static/images/artwork/" + self.player.current_track["id"] + ".png"
            self.player.play(next_song)
            notifiers.notify_new_song_playing(self.service_state())
            self.state["playing"] = True
        else:
            if self.state["playing"]:
                self.player.stop()
                notifiers.notify_no_song_playing(self.service_state())
                self.state["playing"] = False
                if self.player.current_track != None:
                    self.artwork_delete_queue.append(os.getcwd() + self.player.current_track["thumbnail_url"]) 
                self.player.current_track = None


    '''
    PLAYER CONTROLS
    '''
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

    '''
    ARTWORK MANAGEMENT 
    '''
    def artwork_downloader_thread(self):
        while True:
            if len(self.artwork_download_queue) != 0:
                url = self.artwork_download_queue.pop(0)
                try:
                    self.download_artwork(url)
                    notifiers.notify_artwork_available(self.service_state())
                except:
                    pass
            if len(self.artwork_delete_queue) != 0:
                f = self.artwork_delete_queue.pop(0)
                os.remove(f)
            time.sleep(self.PLAYER_UPDATE_INTERVAL)

    def get_artwork(self, track):
        self.artwork_download_queue.append({"url": track["thumbnail_url"], "id": track["id"]})

    def download_artwork(self, download_info):
        urlretrieve(download_info["url"], os.getcwd() + "/static/images/artwork/" + download_info["id"] + ".png")
