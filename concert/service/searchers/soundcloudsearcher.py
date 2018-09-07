import soundcloud
from concert.service.searchers import Searcher

class SoundcloudSearcher(Searcher):
    def __init__(self, config):
        self.client = soundcloud.Client(client_id=config['api_key'])

    def search(self, query, part, max_results):
        # Get SoundCloud results
        sc_tracks = []
        tracks = self.client.get('/tracks.json', q=query, limit=max_results)
        for track in tracks:
            if track.artwork_url == None:
                track.artwork_url = ""
            sc_track = {
                "id": track.id,
                "snippet": {
                    "thumbnails": {"high": {"url": track.artwork_url}},
                    "title": track.title,
                    "url": track.permalink_url
                },
                "trackType": "SoundCloud"
            }
            sc_tracks.append(sc_track)
        return sc_tracks