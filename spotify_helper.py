import os
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
os.environ['SPOTIPY_CLIENT_ID'] = '83ee334a37b24eb586bfd432c3579123'#get yours at https://developer.spotify.com/documentation/general/guides/authorization/app-settings/
os.environ['SPOTIPY_CLIENT_SECRET'] = '7b2107f6952f4d9ea131de9d173045ec' #get yours at https://developer.spotify.com/documentation/general/guides/authorization/app-settings/
os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.com/'

def change_scope(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	return sp

def get_liked_tracks(sp):
	#gets all songs from liked
	more_songs = True
	off_parm = 0
	tracks = []
	tracks_ids = []

	#while loop to get all songs by 50 jumps
	while more_songs:
		cur_results = sp.current_user_saved_tracks(limit=50,offset=off_parm)
		if len(cur_results['items']) < 50:
			more_songs = False
		else:
			off_parm += 50
		for item in cur_results['items']:
			tracks_ids.append(item['track']['id'])
			tracks.append(item['track']['name'])
	
	return tracks_ids, tracks

def create_playlist(sp, name):
	user_id = sp.me()['id']
	playlist = sp.user_playlist_create(
		user= user_id,
		name= name,
		public=True,
		collaborative=False,
		description='Produced By Python, Yay!')
	playlist_id = playlist['id']
	return playlist_id

def get_tracks_by_playlist(sp, playlist_id,order_details=False):

	#gets all songs from desired playlist
	more_songs = True
	off_parm = 0
	tracks_names = []
	tracks_ids = []

	#for removing duplicates
	tracks = []

	#while loop to get all songs by 50 jumps
	while more_songs:
		#get 100 max songs from playlist
		cur_results = sp.playlist_items(playlist_id, limit=50, offset=off_parm)
		if len(cur_results['items']) < 50:
			more_songs = False
		else:
			off_parm += 50
		for pos, item in enumerate(cur_results['items']):
			tracks_ids.append(item['track']['id'])
			tracks_names.append(item['track']['name'])
			tracks.append([item['track']['id'], pos, item['track']])

	if(order_details):
		return tracks
	else:
		return tracks_ids, tracks_names

def add_tracks_to_playlist(sp, playlist_id, fav_tracks_ids):
	while len(fav_tracks_ids) > 50:
		cur_fav_tracks_ids = fav_tracks_ids[:50]
		sp.playlist_add_items(playlist_id,items=cur_fav_tracks_ids)
		fav_tracks_ids = fav_tracks_ids[50:]
		print(fav_tracks_ids)
	sp.playlist_add_items(playlist_id,items=fav_tracks_ids)
	remove_duplicates(sp, playlist_id)

def remove_duplicates(sp, playlist_id):
	user_id = sp.me()['id']
	tracks_ids, tracks_names = get_tracks_by_playlist(sp, playlist_id)
	
	tracks_check = []
	to_remove_ids = []
	#for order details=
	for track_id in tracks_ids:
		if (tracks_ids.count(track_id) > 1) and (to_remove_ids.count(track_id) == 0):
			to_remove_ids.append(track_id)
	print('removing duplicates!')
	scope = 'playlist-modify-public'
	sp = change_scope(scope)
	if len(to_remove_ids) > 0:
		print(to_remove_ids)
		try:
			sp.playlist_remove_all_occurrences_of_items(playlist_id, to_remove_ids)
			sp.playlist_add_items(playlist_id, to_remove_ids)
		except:
			print('error - too many dups, bye')
	return sp

def main():
	#defining scope for reading
	scope = "user-library-read"
	sp = change_scope(scope)
	#getting costumer order
	question = '''hello! Welcome to python spotify helper :), In order to proceed please enter one of these:
	copy - to copy playlist's tracks to another playlist
	like - to copy liked tracks to playlist
	remove - to remove duplicates from playlist\n'''
	from_order = input(question)
	while from_order not in ['copy', 'like','remove']:
		print('Wrong input. try again....')
		time.sleep(1)
		from_order = input(question)
	if (from_order == 'copy'):
		#get playlist tracks
		playlist_id = input('enter playlist id to copy tracks from (url) \n')
		fav_tracks_ids, fav_tracks = get_tracks_by_playlist(sp, playlist_id)
	elif (from_order == 'like'):
		#get liked songs ids and names
		fav_tracks_ids, fav_tracks = get_liked_tracks(sp)
	elif (from_order == 'remove'):
		print('hi!')
		playlist_id = input('enter playlist for duplicates remove (url) \n')
		sp = remove_duplicates(sp, playlist_id)
		print('success')
		exit()

	print('fav tracks: ')
	print('{fav}'.format(fav = fav_tracks).encode('utf-8').decode('utf-8'))
	
	#change scope
	scope = "playlist-modify-public "
	sp = change_scope(scope)

	dest_order = input("What's your destination? N - New Playlist, E - Existing playlist ")
	while dest_order not in ['N', 'E']:
		print('Wrong input. try again....')
		dest_order = input("What's your destination? N - New Playlist, E - Existing playlist ")
	if dest_order == 'N':
		#move to New playlist
		print('Creating new Playlist. ')
		dec_name = input("do u want to set the playlist name? 'Y' - yes, 'N' - no ")
		if dec_name=='Y':
			name = input('enter name ')
		else:
			name = 'python best playlist'
		playlist_id = create_playlist(sp, name)
	elif dest_order == 'E':
		#move to already exists playlist
		playlist_id = input('enter dest_playlist id to copy tracks to (url) ')

	#add tracks to playlist
	add_tracks_to_playlist(sp, playlist_id, fav_tracks_ids)

	print('Success! :)')
	time.sleep(2)




if __name__ == '__main__':
	main()
