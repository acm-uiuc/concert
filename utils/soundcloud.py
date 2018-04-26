import soundcloud
from config import config

# Setup Soundcloud API
sc_client = soundcloud.Client(client_id=config['SOUNDCLOUD_CLIENT_ID'])

MAX_RESULTS = 10

def get_sc_object(url):
    """Gets a soundcloud object based on the url

    The API reference can be found here: https://developers.soundcloud.com/docs/api/reference#resolve

    Args:
        url (str): url of the object to resolve
    Returns:
        soundcloud object
    """
    return sc_client.get('/resolve', url=url)

def get_sc_playlist(id):
    """Gets a soundcloud playlist based on the id of the playlist

    Args:
        id (int): id of the playlist
    Returns:
        List of soundcloud tracks with the stream object replaced by the url of the stream
    """
    sc_tracks = sc_client.get('/playlists/' + str(id)).tracks
    for sc_track in sc_tracks:
        sc_track["stream"] = sc_client.get(sc_track["stream_url"], allow_redirects=False).location
    return sc_tracks

def get_sc_track(id):
    """Gets a soundcloud track based on the id of the track

    Args:
        id (int): id of the track
    Returns:
        Soundcloud track with the stream object replaced by the url of the stream
    """
    sc_track = sc_client.get('/tracks/' + str(id)).fields()
    sc_track["stream"] = sc_client.get(sc_track["stream_url"], allow_redirects=False).location
    return sc_track

def search_sc_tracks(q, limit=MAX_RESULTS):
    """Search soundcloud for tracks based on a user given query

    Args:
        q (str): search query
        limit (int, optional): Max number of results to retrieve. Defaults to MAX_RESULTS const.
    Returns:
        List of formatted soundcloud tracks
    """
    tracks = sc_client.get('/tracks.json', q=q, limit=limit)
    return [format_sc_search_result(track.fields()) for track in tracks]

def format_sc_search_result(track, title=None, url=None):
    """Formats a soundcloud track to be displayed to the client

    Args:
        track (dict): Soundcloud track object in dictionary form to format
        title (str, optional): Title to use in the formatted object. Defaults to the title given in track
        url (str, optional): Url to use in formatted object. Defaults to the url given in track
    Returns:
        Dictionary representing the formatted result
    """
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