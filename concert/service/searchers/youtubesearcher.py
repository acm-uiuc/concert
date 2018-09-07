import requests
from concert.service.searchers import Searcher

class YoutubeSearcher(Searcher):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    def __init__(self, config):
        self.key = config["api_key"]

    def search(self, query, part, max_results):
        # Get Youtube Serach results
        search_url  = self.base_url + "/?q=" + query + "&part=" + part + "&maxResults=" + max_results + "&key=" + self.key
        resp = requests.get(search_url)
        yt_tracks_temp = resp.json()["items"]
        yt_tracks = []
        for track in yt_tracks_temp:
            try:
                vid = track["id"]["videoId"]
                yt_track = {
                    "id": vid,
                    "snippet": track["snippet"],
                    "trackType": "YouTube"
                }
                yt_tracks.append(yt_track)
            except:
                pass
        return yt_tracks