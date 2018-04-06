import os
import unittest
import pafy
import soundcloud
from pymongo import MongoClient
from config import config
from downloader import _get_yt_song, _get_sc_song, _add_song_to_queue, _get_queue, _download_thumbnail, _file_exists

# Setup Soundcloud
SOUNDCLOUD_CLIENT_ID = config["SOUNDCLOUD_CLIENT_ID"]
sc_client = soundcloud.Client(client_id=SOUNDCLOUD_CLIENT_ID)

class SongParseMethods(unittest.TestCase):

	'''
	Test to make sure Pafy is working
	'''
	def test_pafy_online(self):
		url = 'https://www.youtube.com/watch?v=ygS_Cwng7IU'
		video = pafy.new(url)
		assert(video is not None)

	'''
	Test to make sure Pafy is retrieving songs properly
	'''
	def test_yt_song_retrieval(self):
		url = 'https://www.youtube.com/watch?v=ygS_Cwng7IU'
		video = pafy.new(url)
		sd = _get_yt_song(video)
		self.assertEqual(sd["song_title"], "God's Plan")
		self.assertEqual(sd["song_id"], "ygS_Cwng7IU")
		self.assertEqual(sd["song_duration"], 199000)
		self.assertEqual(sd["thumbnail_url_1"], "https://i.ytimg.com/vi/ygS_Cwng7IU/maxresdefault.jpg")
		self.assertEqual(sd["thumbnail_url_2"], "https://i.ytimg.com/vi/ygS_Cwng7IU/mqdefault.jpg")

	'''
	Test to make sure SoundCloud is retrieving songs properly
	'''
	def test_sc_song_retrieval(self):
		url = 'https://soundcloud.com/chancetherapper/chance-the-rapper-the-social'
		sc_object = sc_client.get('/resolve', url=url)
		track = sc_client.get('/tracks/' + str(sc_object.id)).fields()
		sd = _get_sc_song(track)
		self.assertEqual(sd["song_title"], "Chance The Rapper & The Social Experiment - Home Studio ( Back Up In This Bitch)")
		self.assertEqual(sd["song_id"], 141310162)
		self.assertEqual(sd["song_duration"], 138251)
		self.assertEqual(sd["thumbnail_url_1"], 'https://i1.sndcdn.com/artworks-000099111049-o689tj-t500x500.jpg')
		self.assertEqual(sd["thumbnail_url_2"], 'https://i1.sndcdn.com/artworks-000099111049-o689tj-crop.jpg')

	'''
	Test to make sure the queue retrieval is working
	'''
	def test_get_queue(self):
		url = 'https://www.youtube.com/watch?v=ygS_Cwng7IU'
		video = pafy.new(url)
		sd = _get_yt_song(video)

		client = MongoClient()
		db = client.concert_test
		db.Queue.delete_many({})

		_add_song_to_queue(sd, "test", db)
		cur_queue = _get_queue(db)
		assert(cur_queue is not None)

	'''
	Test to make sure adding to the queue works
	'''
	def test_add_to_queue(self):
		url = 'https://www.youtube.com/watch?v=ygS_Cwng7IU'
		video = pafy.new(url)
		sd = _get_yt_song(video)

		client = MongoClient()
		db = client.concert_test
		db.Queue.delete_many({})

		_add_song_to_queue(sd, "test", db)
		cur_queue = _get_queue(db)
		top_song = cur_queue[0]
		self.assertEqual(top_song["title"], "God's Plan")

	'''
	Test to make sure downloading thumbnails works
	'''
	def test_download_thumbnail(self):
		url_1 = "https://i.ytimg.com/vi/ygS_Cwng7IU/maxresdefault.jpg"
		url_2 = "https://i.ytimg.com/vi/ygS_Cwng7IU/mqdefault.jpg"
		song_id = "test_song"
		path = _download_thumbnail(url_1, url_2, song_id)
		assert(_file_exists(path))
		os.remove(path)

if __name__ == '__main__':
    unittest.main()