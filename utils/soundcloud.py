import soundcloud
from config import config

# Setup Soundcloud API
sc_client = soundcloud.Client(client_id=config['SOUNDCLOUD_CLIENT_ID'])

MAX_RESULTS = 10

def get_sc_object(url):
    return sc_client.get('/resolve', url=url)

def get_sc_playlist(id):
    sc_tracks = sc_client.get('/playlists/' + str(id)).tracks
    for sc_track in sc_tracks:
        sc_track["stream"] = sc_client.get(sc_track["stream_url"], allow_redirects=False).location
    return sc_tracks

def get_sc_track(id):
    sc_track = sc_client.get('/tracks/' + str(id)).fields()
    sc_track["stream"] = sc_client.get(sc_track["stream_url"], allow_redirects=False).location
    return sc_track

def search_sc_tracks(q):
    tracks = sc_client.get('/tracks.json', q=q, limit=MAX_RESULTS)
    return [parse_sc_track(track.fields()) for track in tracks]

def parse_sc_track(track, title=None, url=None):
    if track["artwork_url"] == None:
        track["artwork_url"] = ""
    if title == None:
        title = track["title"]
    if url == None:
        url = track["permalink_url"]
    sc_track = {
        "id": track["id"],
        "title": title,
        "thumbnail": track["artwork_url"],
        "url": url,
        "trackType": "SoundCloud"
    }
    return sc_track