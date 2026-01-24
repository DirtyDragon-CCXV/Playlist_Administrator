#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Spotify


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

    
    def __get_next_page__(self, token:str) -> list:
        """
        - inner work funtion (RECURSIVE FUNTION)
        
        get the next page from a request to the api
        
        inputs:
            
            
        output:
            container (list) : 
        """
        return None


    def get_user_playlists(self) -> list:
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
                    print("(get_user_playlists)  data location: local cache.")

            except FileNotFoundError:
                if DEBUG == True:
                    print("(get_user_playlists) [ERROR] file not found. using api instead")
                
                USER_PLAYLIST = self.API.current_user_playlists()

                # save cache
                with open(r"cache/sp_user_playlist.cache", "w") as f:
                    json.dump(self.USER_PLAYLIST, f)

        else:
            if DEBUG == True:
                print("(get_user_playlists) data location: API request.")

            USER_PLAYLIST = self.API.current_user_playlists()

        return USER_PLAYLIST

    
    def get_track_info(self, IDs:str|list) -> list:
        """
        get info of the track/s

        input:
            IDs (str|list) : id or ids from the tracks

        output:
            request (list) : the data from the api
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

        if (argum == IDs):
            if DEBUG == True:
                print("(get_track_info) data location: local cache", end="\n\n")
             
            with open(r"cache/sp_track.cache", "r") as local:
                local.readline()
                request = json.load(local)

                return request
        
        else:
            if DEBUG == True:
                print("(get_track_info) data location: API request", end="\n\n")

            request = self.API.tracks(tracks = IDs)

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
            item (dict) : 

        outputs:
            exit_code (int) = 0 for index changed, 1 for Error tried it
        """
        exit_code = 0

        try:
            self.API.playlist_reorder_items(playlist_id = playlist_ID, range_start = input_index, insert_before = output_index)

        except spotipy.SpotifyStateError as e:
            if DEBUG == True:
                print("(change_playlist_item_index) [ERROR]:")
                print(e)
            exit_code = 1

        return exit_code


    def get_playlist_info(self, ID:str) -> dict:
        """
        get basic info from a playlist using its id

        input:
            ID (str) : id of the video to get the info

        output:
            request (dict) : data from youtube api services
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

            # save cache
            with open(r"cache/sp_playlist_info.cache", "w") as local:
                local.write(ID + "\n")
                json.dump(request, local)

            return request


    def search_track(self, query:str, results_size:int = 5) -> dict:
        """
        input:
            query (str) : the query to search

            - optionals
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

# Test

# test funtions and add _next_page_ funtion