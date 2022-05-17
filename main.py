from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


spotify_id = os.getenv('spotify_id')
spotify_pass = os.getenv('spotify_pass')
redirect_uri = 'http://example.com'

user_input = input('Which era of music you want to listen, Type the date in this format: \nYYYY-MM-DD \n')

response = requests.get(f'https://www.billboard.com/charts/hot-100/{user_input}/')
website_sc = response.text

soup = BeautifulSoup(website_sc, 'html.parser')
print('soup created')

# --- Scrapping useful data -> List of Track name & its artist --- #
song_list = soup.find_all(name="h3", class_="u-letter-spacing-0021", id="title-of-a-story")
artist_list = soup.find_all(name='span', class_='u-letter-spacing-0021')
ng_words = ['Songwriter(s):', 'Producer(s):', 'Imprint/Promotion Label:']
song_titles = [title.text.strip() for title in song_list if title.text.strip() not in ng_words]
artist_name = [artists.text.strip() for artists in artist_list]

# --- Spotify Authorization --- #
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=spotify_id,
        client_secret=spotify_pass,
        redirect_uri=redirect_uri,
        scope="playlist-modify-private",
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()['id']
track_uri_list = []

# --- Searching for URIs on spotify -> List of URIs of all track --- #
print('working...')
for i in range(len(song_titles)):
    try:
        query = f'track:{song_titles[i]} artist:{artist_name[i]}'
        search_result = sp.search(q=query, type='track')
        track_uri = search_result['tracks']['items'][0]['id']
        track_uri_list.append(track_uri)
    except IndexError:
        print(f'Song {i}. {song_titles[i]} not found on spotify!')
print('Got all the track URIs')

# --- Creating playlist and adding tracks to it -> None --- #
playlist_name = f'{user_input} Billboard Top 100'
created_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
print(f'Playlist created!')
playlist_id = created_playlist['id']
sp.playlist_add_items(playlist_id, track_uri_list)

print('tracks added to playlist')
print('All done, Yahoo!')

print(f'Open the playlist from here: \nhttps://open.spotify.com/playlist/{playlist_id}')

