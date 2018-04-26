import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
from config import config

# Setup Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=config["SPOTIFY_CLIENT_ID"],
    client_secret=config["SPOTIFY_CLIENT_SECRET"])
sp_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_sp_track(track_id):
    return sp_client.track(track_id)

def parse_sp_track(track):
    artists = [artist["name"] for artist in track["artists"]]
    title = track["name"] + " - " + ', '.join(artists)
    if len(track["album"]["images"]) > 0:
        thumbnail = track["album"]["images"][0]["url"]
    else:
        thumbnail = ""
    sp_track = {
        "id": track["id"],
        "title": title,
        "thumbnail": thumbnail,
        "url": track["uri"],
        "trackType": "Spotify"
    }
    return sp_track

def get_sp_playlist(url, fields, only_tracks=False):
    o = urlparse(url)
    path = o.path
    username = path.split('/')[2]
    playlist_id = path.split('/')[4]
    if not only_tracks:
        return sp_client.user_playlist(username, playlist_id, fields=fields)
    else:
        return sp_client.user_playlist_tracks(username, playlist_id, fields=fields)

def format_sp_playlist_result(url):
    playlist = get_sp_playlist(url, "images,name,id")
    playlist_object = {
        "id": playlist["id"],
        "thumbnail": playlist["images"][0]["url"],
        "title": playlist["name"],
        "url": url,
        "trackType": "SpotifyPlaylist"
    }
    return playlist_object

def search_sp_tracks(q, limit=5):
    tracks = sp_client.search(q=q, type='track', limit=limit)["tracks"]["items"]
    return [parse_sp_track(track) for track in tracks]

def extract_sp_track_info(sp_track):
    spotify_track = {}
    spotify_track["name"] = sp_track["name"]
    spotify_track["artists"] = [artist["name"] for artist in sp_track["artists"]]
    if len(sp_track["album"]["images"]) > 0:
        spotify_track["art"] = sp_track["album"]["images"][0]["url"]
    else:
        spotify_track["art"] = ""
    return spotify_track