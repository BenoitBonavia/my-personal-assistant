import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyManager:
    """
    This class is used to manage the music in the how through Spotify with the Spotify API
    """

    def __init__(self):
        sp_oauth = SpotifyOAuth(
            client_id=os.getenv('SPOTIPY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
            scope="user-library-read user-read-playback-state",
        )
        print("Please visit this URL: {0}".format(sp_oauth.get_authorize_url()))
        self.spotify = spotipy.Spotify(auth_manager=sp_oauth)

    def get_saved_tracks(self):
        results = self.spotify.current_user_saved_tracks()
        print(results)

    def play_song(self, song_title, song_artist=None):
        """
        Play a song on the Spotiy account connected that has the specified title and artist

        Parameters:
        song_title (str): Title of the song to play
        song_artist (str, optional): Artist of the song to play
        """
        results = self.spotify.search(q=f'track:{song_title} artist:{song_artist}', type='track')
        if len(results['tracks']['items']) > 0:
            song_uri = results['tracks']['items'][0]['uri']
            self.spotify.start_playback(uris=[song_uri])
            return f"Playing {song_title} by {song_artist}"

    def get_devices(self):
        """ Get list of devices connected to the Spotify account """
        return self.spotify.devices()
