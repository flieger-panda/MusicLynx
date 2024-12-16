import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

for song in sp.search(q="BURN", type="track", limit=10)["tracks"]["items"]:
    artists = ""
    print(song['artists'][0]["name"])
    break