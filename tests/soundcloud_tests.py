import unittest
from utils.soundcloud import *

class SoundcloudUtilsTest(unittest.TestCase):
	
	def test_get_sc_object(self):
		"""
		Test to see if soundcloud is retrieiving the correct souncloud object
		"""
		url = "https://soundcloud.com/marshmellomusic/alone"
		sc_object = get_sc_object(url).fields()
		self.assertEqual(sc_object["kind"], "track")
		self.assertEqual(sc_object["id"], 264023874)

	def test_get_sc_playlist(self):
		"""
		Tests to see if soundcloud is retrieving playlists correctly
		"""
		url = "https://soundcloud.com/tommy-yu-3/sets/test"
		sc_object = get_sc_object(url).fields()
		playlist_id = sc_object["id"]
		playlist = get_sc_playlist(playlist_id)
		first_track = playlist[0]
		self.assertEqual(len(playlist), 2)
		self.assertEqual(first_track["id"], 90243759)

	def test_get_sc_track(self):
		"""
		Tests to see if soundcloud is retrieving tracks correctly
		"""
		track_id = 90243759
		track = get_sc_track(track_id)
		self.assertEqual(track["title"], "Favorite Song (ft. Childish Gambino)")
		self.assertEqual(track["id"], 90243759)

if __name__ == '__main__':
    unittest.main()