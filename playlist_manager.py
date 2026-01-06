"""
/.

Main python file for the proyect "Playlist_Manager"
"""

import os, sys

# python3 app.py [-yt, -sp, -c] [-s (A1 | A2), -u, -r] <url>
ARGUMENTS = sys.argv[1:]

print(ARGUMENTS)

# --- Youtube section
if (ARGUMENTS[0] == "-help" or ARGUMENTS[0] == "-h"):
	print("display help")

elif (ARGUMENTS[0] == "-yt"):
	if (ARGUMENTS[1] == "-s"):
		print("yt sort")
	elif (ARGUMENTS[1] == "-u"):
		print("yt update")
	elif (ARGUMENTS[1] == "-r"):
		print("yt review")
	else:
		print("youtube option not valid...")

# --- Spotify section
elif (ARGUMENTS[0] == "-sp"):
	if (ARGUMENTS[1] == "-s"):
		print("sp sort")
	elif (ARGUMENTS[1] == "-u"):
		print("sp update")
	elif (ARGUMENTS[1] == "-r"):
		print("sp review")
	else:
		print("spotify option not valid...")
else:
	print("option not valid...")