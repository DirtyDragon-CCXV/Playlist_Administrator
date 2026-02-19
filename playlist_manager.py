#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Spotify

"""
./playlist_manager.py

Main python file for the project "Playlist_Manager"
"""

import re
import json
import os, sys
import sqlite3 as sq
from spotify_api import Spotify
from youtube_music_api import Youtube


# --- Youtube modules ---
def youtube_update_database(LOCAL_ID:str):
	YT = Youtube()

	if DEBUG == True:
		playlist_data = YT.get_playlist_info(ID = LOCAL_ID)

		PLAYLIST_NAME = playlist_data["items"][0]["snippet"]["title"]
		playlist_length = playlist_data["items"][0]["contentDetails"]["itemCount"]

		print("[INFO]---> Playlist Name: ", PLAYLIST_NAME)
		print("[INFO]---> Playlist Length: ", playlist_length, end="\n")

		del playlist_data
		del playlist_length
	else: 
		PLAYLIST_NAME = YT.get_playlist_info(ID = LOCAL_ID)["items"][0]["snippet"]["title"]

	playlist = YT.get_playlist_tracks_info(ID = LOCAL_ID)

	tracks_filter = []

	for tr in playlist:
		id_track = tr["id"]

		title = tr["snippet"]["title"]

		artist = tr["snippet"]["channelTitle"]
		artist = re.sub(r"\s-.*", "", artist)

		duration = tr["contentDetails"]["duration"]

		tracks_filter.append( [id_track, title, artist, duration] )
	del playlist


	try:
		with sq.connect("db/youtube.db") as db:
			cursor = db.cursor()

			table_exist = len(cursor.execute(f"""SELECT * FROM sqlite_master WHERE name='{PLAYLIST_NAME}'""").fetchall())

			# if the table is already created
			if table_exist == 1:
				for track in tracks_filter:
					cursor.execute(f"INSERT INTO \"{PLAYLIST_NAME}\" VALUES (?, ?, ?, ?)", (track[0], track[1], str(track[2]), track[3]))

			else:
				cursor.execute(f"""CREATE TABLE "{PLAYLIST_NAME}" ("ID" TEXT, "NAME" TEXT, "ARTIST" TEXT, "TIME" TEXT)""")

				for track in tracks_filter:
					cursor.execute(f"INSERT INTO \"{PLAYLIST_NAME}\" VALUES (?, ?, ?, ?)", (track[0], track[1], str(track[2]), track[3]))
				
			print("[OK]---> Database updated.\n")

	except sq.OperationalError:
		print("[ERROR]---> Database is used by another app.\n")
		exit(1)



# --- Spotify modules ---
def spotify_update_database(LOCAL_ID:str):
	SP = Spotify()

	playlist = SP.get_playlist_info(ID = LOCAL_ID)

	if DEBUG == True:
		PLAYLIST_NAME = playlist["name"]
		playlist_length = playlist["tracks"]["total"]

		print("[INFO]---> Playlist Name: ", PLAYLIST_NAME)
		print("[INFO]---> Playlist Length: ", playlist_length, end="\n")

		del playlist_length
	else: 
		PLAYLIST_NAME = playlist["name"]

	tracks_filter = []

	for tr in playlist["tracks"]["items"]:
		id_track = tr["track"]["id"]

		title = tr["track"]["name"]

		artist = []
		for art in tr["track"]["artists"]:
			artist.append(art["name"])

		duration = tr["track"]["duration"]

		tracks_filter.append( [id_track, title, artist, duration] )
	del playlist


	try:
		with sq.connect("db/spotify.db") as db:
			cursor = db.cursor()

			table_exist = len(cursor.execute(f"""SELECT * FROM sqlite_master WHERE name='{PLAYLIST_NAME}'""").fetchall())

			# if the table is already created
			if table_exist == 1:
				for track in tracks_filter:
					cursor.execute(f"INSERT INTO \"{PLAYLIST_NAME}\" VALUES (?, ?, ?, ?)", (track[0], track[1], str(track[2]), track[3]))

			else:
				cursor.execute(f"""CREATE TABLE "{PLAYLIST_NAME}" ("ID" TEXT, "NAME" TEXT, "ARTIST" TEXT, "TIME" TEXT)""")

				for track in tracks_filter:
					cursor.execute(f"INSERT INTO \"{PLAYLIST_NAME}\" VALUES (?, ?, ?, ?)", (track[0], track[1], str(track[2]), track[3]))
				
			print("[OK]---> Database updated.\n")

	except IndexError:
		print("[ERROR]---> Database is used by another app.\n")
		exit(1)


# python3 app.py [-yt, -sp, -c] [-s (A1 | A2), -u, -r] <url>
DEBUG = True
ARGUMENTS = sys.argv[1:]

print(ARGUMENTS)

# --- Youtube section
if (ARGUMENTS[0] == "-help" or ARGUMENTS[0] == "-h"):
	print("display help")

elif (ARGUMENTS[0] == "-yt"):
	if (ARGUMENTS[1] == "-s"):
		print("yt sort")


	elif (ARGUMENTS[1] == "-u"):
		try:
			youtube_update_database(LOCAL_ID = ARGUMENTS[2])

		except IndexError:
			with open("cache/user_playlist.json", "r") as f:
				user_playlist = json.load(f)["youtube"]

			for i in user_playlist:
				youtube_update_database(LOCAL_ID = i[0])

	elif (ARGUMENTS[1] == "-r"):
		print("yt review")

	else:
		print("youtube option not valid...")

# --- Spotify section
elif (ARGUMENTS[0] == "-sp"):
	if (ARGUMENTS[1] == "-s"):
		print("sp sort")

	elif (ARGUMENTS[1] == "-u"):
		try:
			spotify_update_database(LOCAL_ID = ARGUMENTS[2])

		except IndexError:
			with open("cache/user_playlist.json", "r") as f:
				user_playlist = json.load(f)["spotify"]

			for i in user_playlist:
				spotify_update_database(LOCAL_ID = i[0])

	elif (ARGUMENTS[1] == "-r"):
		print("sp review")
	else:
		print("spotify option not valid...")
else:
	print("option not valid...")