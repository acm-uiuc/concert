from abc import ABC, abstractmethod

class Fetcher(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def fetch_song(self, url):
        pass

    @abstractmethod
    def process_track_info(self, track):
        pass