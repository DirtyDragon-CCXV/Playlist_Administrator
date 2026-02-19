#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Spotify

"""
./spotify_api.py

Module to simplify the interaction with the Spotify API
"""

import os, json
import spotipy
from spotipy.oauth2 import SpotifyOAuth


# --- constants
SCOPE = "user-library-read" #for only test uses 'user-library-read'
DEBUG = True
USES_API_CACHE = True

# --- inner work
with open(r"debug/spotify_client_id.json", "r") as f:
    data = json.load(f)

    USER_ID = data["client_id"]
    USER_SECRET = data["client_secret"]



class Spotify():
    def __init__ (self):
        self.API = spotipy.Spotify( auth_manager = SpotifyOAuth(
                                                    client_id = USER_ID,
                                                    client_secret = USER_SECRET,
                                                    scope = SCOPE,
                                                    redirect_uri = "http://127.0.0.1:8888/callback"
                                                    )
        )

        if DEBUG == True:
            print("Login... ok")


    def __format_duration__ (self, time:str) -> str:
        """
        - inner work funtion

        Change the format from miliseconds to MM:SS

        input:
            time (str) : the duration in ms

        output:
            str : the duration with the format
        """
        time = int(time) // 1000

        minutes = time / 60
        seconds = int( (minutes - int(minutes)) * 60)

        if seconds < 10:
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)

        return str( int(minutes) ) + ":" + seconds


    def __get_next_page__(self, previous_request:str) -> list:
        """
        - inner work funtion

        get the next page from a request to the api

        inputs:
            previous_request (dict) : previous petition to the api to extract the 'next' href

        output:
            tracks (list) : almost all the tracks from the playlist

        @with the help of: ackleyrc (https://stackoverflow.com/a/39113522/31846403)
        """
        tracks = []

        while previous_request.get("next") != None:
            previous_request = self.API.next(previous_request)

            tracks.extend(previous_request['items'])

        return tracks


    def get_user_playlists(self, save_as_file:bool = False) -> list:
        """
        get the library from the user

        output:
            USER_PLAYLIST (list) : each playlist in dict format
        """
        if USES_API_CACHE == True:
            try:
                with open(r"cache/sp_user_playlist.cache", "r") as f:
                    USER_PLAYLIST = json.load(f)

                if DEBUG == True:
                    print("(get_user_playlists) username:", USER_PLAYLIST["items"][0]["owner"]["display_name"])
                    print("(get_user_playlists) data location: local cache.")

            except FileNotFoundError:
                if DEBUG == True:
                    print("(get_user_playlists) [ERROR] file not found. using api instead")

                USER_PLAYLIST = self.API.current_user_playlists()

                if DEBUG == True:
                    print("(get_user_playlists) username:", USER_PLAYLIST["items"][0]["owner"]["display_name"])

                # save cache
                with open(r"cache/sp_user_playlist.cache", "w") as f:
                    json.dump(USER_PLAYLIST, f)

        else:
            if DEBUG == True:
                print("(get_user_playlists) data location: API request.")

            USER_PLAYLIST = self.API.current_user_playlists()

            if DEBUG == True:
                print("(get_user_playlists) username:", USER_PLAYLIST["items"][0]["owner"]["display_name"])

        if save_as_file == True:
            cache = []
            # extract only the ids and names from playlists
            for x in USER_PLAYLIST["items"]:
                cache.append((x["id"], x["name"]))

            try:
                with open("cache/user_playlist.json", "r") as f:
                    data = json.load(f)

                data["spotify"] = cache

                with open("cache/user_playlist.json", "w") as f:
                    json.dump(data, f)
                    
            except FileNotFoundError:
                data = {"spotify" : cache}

                with open("cache/user_playlist.json", "w") as f:
                    json.dump(data, f)

        return USER_PLAYLIST


    def get_track_info(self, IDs:str|list) -> dict or list:
        """
        get info of the track/s

        input:
            IDs (str|list) : id or ids from the tracks [max 100 ids]

        output:
            request (dict|list) : the data/s from the api
        """
        if DEBUG == True:
            print(f"(get_track_info) ID/s : {IDs}")

        if type(IDs) == str:
            IDs = [IDs]

        argum = None
        if USES_API_CACHE == True:
            try:
                with open(r"cache/sp_track.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                if DEBUG == True:
                    print("(get_track_info) [ERROR] file not found. using api instead")

        if (argum == str(IDs)):
            if DEBUG == True:
                print("(get_track_info) data location: local cache", end="\n\n")

            with open(r"cache/sp_track.cache", "r") as local:
                local.readline()
                request = json.load(local)

        else:
            if DEBUG == True:
                print("(get_track_info) data location: API request", end="\n\n")

            request = self.API.tracks(tracks = IDs)

            if len(request["tracks"]) == 1:
                request = request["tracks"][0]

                new_value = self.__format_duration__(time = request["duration_ms"])

                del request["duration_ms"]
                request["duration"] = new_value

            else:
                for i in request["tracks"]:
                    new_value = self.__format_duration__(time = i["duration_ms"])

                    del i["duration_ms"]
                    i["duration"] = new_value

            # save cache
            with open(r"cache/sp_track.cache", "w") as local:
                local.write(str(IDs) + "\n")
                json.dump(request, local)

        return request


    def change_playlist_item_index(self, playlist_ID:str, input_index:int, output_index:int) -> int:
        """
        change the index from a item, inner the playlist.

        inputs:
            playlist_ID (str) : Id of the playlist that the track its in
            input_index (int) : index of the track to be move (the index where is the song)
            output_index (int) : index of track where should insert before (the index where its be inserted)

        outputs:
            exit_code (int) = 0 for index changed, 1 for Error tried it
        """
        exit_code = 0

        try:
            self.API.playlist_reorder_items(
                        playlist_id = playlist_ID,
                        range_start = input_index,
                        insert_before = output_index
            )

        except spotipy.exceptions.SpotifyException as e:
            if DEBUG == True:
                print("\n(change_playlist_item_index) [ERROR]:")
                print(e)

            exit_code = 1

        return exit_code


    def get_playlist_info(self, ID:str) -> dict:
        """
        get the info from a playlist using its id, included tracks info

        input:
            ID (str) : id of the playlist to get the info

        output:
            request (dict) : data from spotify api services
        """

        if DEBUG == True:
            print(f"(get_playlist_info) playlist ID : {ID}")

        argum = None
        if USES_API_CACHE == True:
            try:
                with open(r"cache/sp_playlist_info.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                if DEBUG == True:
                    print("(get_playlist_info) [ERROR] file not found. using api instead")

        if (argum == ID):
            if DEBUG == True:
                print("(get_playlist_info) data location: local cache", end="\n\n")

            with open(r"cache/sp_playlist_info.cache", "r") as local:
                local.readline()
                content = json.load(local)

            return content

        else:
            if DEBUG == True:
                print("(get_playlist_info) data location: API request", end="\n\n")

            request = self.API.playlist(playlist_id = ID)

            # get the rest of tracks
            if request["tracks"].get("next"):
                tracks = self.__get_next_page__(request["tracks"])

                request["tracks"]["items"] += tracks

            # change duration format
            for i in request["tracks"]["items"]:
                new_value = self.__format_duration__(time = i["track"]["duration_ms"])

                del i["track"]["duration_ms"]
                i["track"]["duration"] = new_value

            # save cache
            with open(r"cache/sp_playlist_info.cache", "w") as local:
                local.write(ID + "\n")
                json.dump(request, local)

            return request


    def search_track(self, query:str, results_size:int = 5) -> dict:
        """
        input:
            query (str) : the query to search

            - optionals:
            results_size (int) : the maximun results for page, by default is five [max is 50]

        output:
            request (dict) : a page of search
        """
        if DEBUG == True:
            print(f"(search_track) Query : {query}")

        argum = None
        metadata = str([query, results_size])
        if USES_API_CACHE == True:
            try:
                with open(r"cache/sp_search.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                if DEBUG == True:
                    print("(search_track) [ERROR] file not found. using api instead")

        if (argum == metadata):
            if DEBUG == True:
                print("(search_track) data location: local cache", end="\n\n")

            with open(r"cache/sp_search.cache", "r") as local:
                local.readline()
                content = json.load(local)

            return content

        else:
            if DEBUG == True:
                print("(search_track) data location: API request", end="\n\n")

            request = self.API.search( q = query, limit = results_size, type = "track")

            # save cache
            with open(r"cache/sp_search.cache", "w") as local:
                local.write(metadata + "\n")
                json.dump(request, local)

        return request