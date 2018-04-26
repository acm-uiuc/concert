import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse
from config import config

# Setup Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=config["SPOTIFY_CLIENT_ID"],
    client_secret=config["SPOTIFY_CLIENT_SECRET"])
sp_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_sp_track(track_id):
    """Retrieves Spotify track based on track id

    Args:
        id (str): id of the track
    Returns:
        Spotify track object
    """
    return sp_client.track(track_id)

def format_sp_search_result(track):
    """Formats a spotify track to be displayed to clients

    Args:
        track (dict): Spotify track 
    Returns:
        Formatted version of the spotify track
    """
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
    """Gets a spotify playlist dict 

    Args:
        url (str): Url of the spotify playlist
        fields (str): Fields of the playlist to retrieve. Please look here for further documenation: 
            https://beta.developer.spotify.com/documentation/web-api/reference/playlists/get-playlist/
        only_tracks (bool, optional): Bool to determine whether or not to only retireve the tracks or include
            meta_data of the playlist as well
    Returns:
        Dictionary containing the spotify playlist info
    """
    o = urlparse(url)
    path = o.path
    username = path.split('/')[2]
    playlist_id = path.split('/')[4]
    if not only_tracks:
        return sp_client.user_playlist(username, playlist_id, fields=fields)
    else:
        return sp_client.user_playlist_tracks(username, playlist_id, fields=fields)

def format_sp_playlist_result(url):
    """Formats a spotify playlist to be displayed to clients

    Args:
        url (str): url of the playlist
    Returns:
        Dictionary of the formatted playlist
    """
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
    """Searches spotify for tracks based on user query

    Args:
        q (str): User query
        limit (int, optional): Limit of number of results to retrieve
    Returns:
        List of formatted spotify tracks
    """
    tracks = sp_client.search(q=q, type='track', limit=limit)["tracks"]["items"]
    return [format_sp_search_result(track) for track in tracks]

def extract_sp_track_info(sp_track):
    """Extracts neccessary fields from a spotify dict returned from spotipy

    Args:
        sp_track (dict): Dictionary of spotify track returned from a spotipy api call.
    Returns:
        Dict of all the neccessary info from sp_track
    """
    spotify_track = {}
    spotify_track["name"] = sp_track["name"]
    spotify_track["artists"] = [artist["name"] for artist in sp_track["artists"]]
    if len(sp_track["album"]["images"]) > 0:
        spotify_track["art"] = sp_track["album"]["images"][0]["url"]
    else:
        spotify_track["art"] = ""
    return spotify_track