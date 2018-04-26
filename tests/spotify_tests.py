import unittest
from utils.spotify import *

class SpotifyUtilsTest(unittest.TestCase):

	def test_get_sp_track(self):
		'''
		Tests to see if the spotipy client can retrieve songs.
		Uses Waves by Kanye West as the reference url.
		'''
		track_id = '3nAq2hCr1oWsIU54tS98pL'
		track = get_sp_track(track_id)
		self.assertEqual(track['id'], '3nAq2hCr1oWsIU54tS98pL')
		self.assertEqual(track['name'], 'Waves')
	
	def test_get_sp_playlist(self):
		'''
		Test to see if spotipy is retrieving the correct playlists
		'''
		url = 'https://open.spotify.com/user/1230457405/playlist/6mes1NJg3vzvpr4VefrcWu?si=EQr_MPIVRQqI7upz-crYTA'
		playlist = get_sp_playlist(url, '')
		self.assertEqual(playlist['name'], 'Concert - Test')
		self.assertEqual(len(playlist['tracks']['items']), 3)

	def test_search_sp_tracks(self):
		'''
		Tests to see if Spotify search is working
		'''
		q = "Childish Gambino"
		tracks = search_sp_tracks(q, 10)
		assert tracks is not None
		self.assertEqual(len(tracks), 10)

	def test_extract_sp_track_info(self):
		'''
		Tests to see if spotify utils are extracting info properly
		'''
		track_id = '3nAq2hCr1oWsIU54tS98pL'
		track = get_sp_track(track_id)
		extracted_info = extract_sp_track_info(track)
		expected_info = {'name': 'Waves', 'art': 'https://i.scdn.co/image/443372cd2c6d4245833fb46ac1c5dabca00c78a9', 'artists': ['Kanye West']}
		self.assertDictEqual(extracted_info, expected_info)

if __name__ == '__main__':
    unittest.main()