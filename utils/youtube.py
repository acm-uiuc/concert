import requests
import pafy
from config import config

yt_key = config['YT_API_KEY']

YT_BASE_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_THUMBNAIL_URL = 'https://i.ytimg.com/vi/'
MAXRES_THUMBNAIL = '/maxresdefault.jpg'
MQ_THUMBNAIL = '/mqdefault.jpg'
MAX_RESULTS = 10

def search_yt_video(q, max_results=MAX_RESULTS):
	search_url  = YT_BASE_URL + "/?q=" + q + "&part=snippet&maxResults=" + str(max_results) + "&key=" + yt_key
	resp = requests.get(search_url)
	tracks = resp.json()["items"]
	yt_tracks = []
	for track in tracks:
		try:
			vid = track["id"]["videoId"]
			yt_track = parse_yt_video(vid, track["snippet"])
			yt_tracks.append(yt_track)
		except:
			pass
	return yt_tracks

def parse_yt_video(vid, snippet):
	url = "https://www.youtube.com/watch?v=" + vid
	yt_track = {
		"id": vid,
		"title": snippet["title"],
		"thumbnail": snippet["thumbnails"]["high"]["url"],
		"url": url,
		"trackType": "YouTube"
	}
	return yt_track

def parse_yt_playlist(yt_playlist, q):
	first_song = yt_playlist["items"][0]["pafy"]
	thumbnail_url = "{}{}{}".format(YOUTUBE_THUMBNAIL_URL, first_song.videoid, MQ_THUMBNAIL)
	playlist_object = {
		"id": yt_playlist["playlist_id"],
		"thumbnail": thumbnail_url,
		"title": yt_playlist["title"],
		"url": q,
		"trackType": "YouTubePlaylist"
	}
	return playlist_object

def get_yt_audio(sp_track):
	'''
	Get the audio stream url from the best matching YouTube video
	'''
	# Get the best YouTube match
	query = sp_track["name"] + " - " + " ,".join(sp_track["artists"])
	yt_track = search_yt_video(query, 1)[0]
	# Get Song Info from Pafy
	video_url = "https://www.youtube.com/watch?v=" + yt_track["id"]
	video = pafy.new(video_url)
	return video