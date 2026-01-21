#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Google


import os, json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.errors import HttpError as google_HttpError


# --- other data
NUMS = [str(i) for i in range(10)]

# --- contants
SCOPES = ['https://www.googleapis.com/auth/youtube'] #for test only, use "https://www.googleapis.com/auth/youtube.readonly"
DEBUG = True
USES_API_CACHE = True
TOKEN_PATH = r"debug/token.json"
CLIENT_SECRET_PATH = r"debug/client_secret.apps.googleusercontent.com.json"


# --- background work
if os.path.exists(r"cache") == False:
    os.makedirs(r"cache")

try:
    with open(TOKEN_PATH) as f:
        data = json.load(f)
        if data["scopes"] != SCOPES:
            os.remove(TOKEN_PATH)
            print("(WARNING) Token deleted because the SCOPES was changed.")
except FileNotFoundError:
    print("(WARNING) Token JSON was not found.")



class Youtube():
    def __init__ (self, token_path:str = TOKEN_PATH, client_secret_path:str = CLIENT_SECRET_PATH):
        """
        use or create the token json file to use the Oauth2 credentials with the api

        inputs:
            token_path (str) : path to open or save the token to access with the api
            client_secret_path (str|None) : path to the client secret json from the google cloud api, only necesary to create the token

        output:
            YOUTUBE (variable) : build to use the youtube api v3

        @with the help of Gemini "Fast" (Google)
        """
        flow = None
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                if DEBUG == True:
                    print("(WARNING) Token is expired, the token will be refreshed.")

                creds.refresh(Request())
            else:
                if DEBUG == True:
                    print("(WARNING) Token is gonna be created.")

                if client_secret_path != None:
                    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("[ERROR] the path of 'client_secret' json is requiered to create the token.")
                    exit(1)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.API = build('youtube', 'v3', credentials=creds)
        del flow
        del creds

        if DEBUG == True:
            print("login... ok")

    def __get_next_page__(self, previous_request:dict, previous_response:dict) -> list:
        """
        - inner work funtion (RECURSIVE FUNTION)
        
        get the next page from a request to the api
        
        inputs:
            previous_request (dict) : previous request to the api
            previous_response (dict) : previous response (what you received) from the api
            
        output:
            container (list) : all pages than possible (less the first page)
        """
        response_get = self.API.playlistItems().list_next(
            previous_request = previous_request,
            previous_response = previous_response
        )
        
        response = response_get.execute()

        content = [response]

        if response.get("nextPageToken") != None:
            other_response = self.__get_next_page__(response_get, response)
            
            #join lists one by ono
            content += other_response

        return content


    def get_video_info(self, ID:str|list) -> list:
        """
        get basic info from a video or videos using its id

        input:
            ID (str | list) : id or a list of ids to get the info

        output:
            request (list) : data from youtube api services
        """

        if DEBUG == True:
            print(f"(get_video_info) ID/s : {ID}")

        argum = None
        if USES_API_CACHE == True:
            try:
                with open(r"cache/video.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                print("(get_video_info) [ERROR] file not found. using api instead")

        if (argum == ID):
            if DEBUG == True:
                print("(get_video_info) data location: local cache", end="\n\n")
             
            with open(r"cache/video.cache", "r") as local:
                local.readline()
                content = json.load(local)

            return content

        else:
            if DEBUG == True:
                print("(get_video_info) data location: API request", end="\n\n")

            if type(ID) == list:
                container  = []

                #if the list of ids its too long (more than 50), the maximun request from the api is 50.
                while len(ID) >= 1:
                    request = self.API.videos().list(
                        id = ID[0:50],
                        part = ["contentDetails", "snippet"],
                        maxResults = 50
                    ).execute()["items"]

                    container += request

                    ID = ID[50:]
                
                request = container

            else:
                request = self.API.videos().list(
                    id = ID,
                    part = ["contentDetails", "snippet"]
                    ).execute()
                
                request = request["items"]
                
            # do some modifications
            for track in request:
                time = []

                for character in track["contentDetails"]["duration"]:
                    if character == "H" or character == "M":
                        time.append(":")
                    elif character in NUMS:
                        time.append(character)
                    elif character == "S":
                        if time[-2] == ":":
                            time.insert(time.index(time[-1]), "0")
                    
                duration = "".join(time)

                track["contentDetails"]["duration"] = duration

            # save cache
            with open(r"cache/video.cache", "w") as local:
                local.write(str(ID) + "\n")
                json.dump(request, local)

            return request


    def get_playlist_tracks_info(self, ID:str) -> dict:
            """
            get basic info about tracks from a playlist using its id

            input:
                ID (str) : id of the video to get the info

            output:
                request (dict) : data from youtube api services with tracks info
            """

            if DEBUG == True:
                print(f"(get_playlist_tracks_info) playlist ID : {ID}")

            argum = None
            if USES_API_CACHE == True:
                try:
                    with open(r"cache/playlist_tracks.cache", "r") as local:
                        argum = local.readline().strip()
                except FileNotFoundError:
                    print("(get_playlist_tracks_info) [ERROR] file not found. using api instead")


            if (argum == ID):
                if DEBUG == True:
                    print("(get_playlist_tracks_info) data location: local cache", end="\n\n")
                
                with open(r"cache/playlist_tracks.cache", "r") as local:
                    local.readline()
                    content = json.load(local)

                return content

            else:
                if DEBUG == True:
                    print("(get_playlist_tracks_info) data location: API request", end="\n\n")

                #get playlist info
                request_one = self.API.playlists().list(
                    id = ID,
                    part = ["contentDetails", "snippet"]
                    ).execute()

                #get the first 50 tracks from the playlist (50 is the max to a request)
                request_two = self.API.playlistItems().list(
                    playlistId = ID,
                    part = ["contentDetails"],
                    maxResults = 50
                    )
                response_two = request_two.execute()

                #extract the first 50 tracks IDs
                tracks = []
                for iterator in response_two["items"]:
                    tracks.append(iterator["contentDetails"]["videoId"])
                
                #get the rest of track IDs using the Token
                if response_two.get("nextPageToken") != None:
                    other_request = self.__get_next_page__(request_two, response_two)

                    for iterator in other_request:
                        for extractor in iterator["items"]:
                            tracks.append(extractor["contentDetails"]["videoId"])

                #get the tracks info usings its IDs
                request_three = self.get_video_info(ID = tracks)

                #join the playlist info with a list of tracks with its info
                request_one["tracks"] = request_three

                # save cache
                with open(r"cache/playlist_tracks.cache", "w") as local:
                    local.write(ID + "\n")
                    json.dump(request_one, local)

                return request_one


    def change_playlist_item_index(self, playlist_id:str, item:dict) -> int:
        # !--> add cache system
        """
        change the index from a item, inner the playlist.

        inputs:
            playlist_id (str) : Id of the playlist that the track its in
            item (dict) : track info (from playlistItems) in the next JSON estructure:
                          {
                            'id' : str,
                            'resource_id' : {
                                'kind' : str,
                                'video_id' : str
                            },
                            'index' : int
                          }

        outputs:
            exit_code (int) = 0 for index changed, 1 for Error tried it
        """
        exit_code = 0

        try:
            request = self.API.playlistItems().update(
                part = ["id", "snippet"],
                body = {
                    "id": item["id"],
                    "snippet": {
                        "playlistId" : playlist_id,
                        "resourceId": {
                            "kind": item["resource_id"]["kind"],
                            "videoId": item["resource_id"]["video_id"],
                        },
                        "position": item["index"],
                    }
                }
            ).execute()
        except google_HttpError as e:
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
                with open(r"cache/playlist_info.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                print("(get_playlist_info) [ERROR] file not found. using api instead")


        if (argum == ID):
            if DEBUG == True:
                print("(get_playlist_info) data location: local cache", end="\n\n")
            
            with open(r"cache/playlist_info.cache", "r") as local:
                local.readline()
                content = json.load(local)

            return content

        else:
            if DEBUG == True:
                print("(get_playlist_info) data location: API request", end="\n\n")

            #get playlist info
            request_one = self.API.playlists().list(
                id = ID,
                part = ["contentDetails", "snippet"]
            ).execute()

            #get the first 50 tracks from the playlist (50 is the max to a request)
            request_two = self.API.playlistItems().list(
                playlistId = ID,
                part = ["snippet"],
                maxResults = 50
            )
            response_two = request_two.execute()

            #extract the first 50 tracks IDs
            tracks = []
            for iterator in response_two["items"]:
                tracks.append(iterator)
            
            #get the rest of track IDs using the Token
            if response_two.get("nextPageToken") != None:
                other_request = self.__get_next_page__(request_two, response_two)

                for iterator in other_request:
                    for extractor in iterator["items"]:
                        tracks.append(extractor)

            #join the playlist info with a list of tracks with its info
            request_one["tracks"] = tracks

            # save cache
            with open(r"cache/playlist_info.cache", "w") as local:
                local.write(ID + "\n")
                json.dump(request_one, local)

            return request_one


    def search_track (self, query:str, type_filter:str|None = "video", from_channel:str|None = None, results_size:int = 5) -> dict:
        """
        input:
            query (str) : the query to search

            - optionals
            type_filter (str | None) : the type of content [channel | playlist | video | music]
            from_channel (str | None) : id of from a channel to only search in its videos
            results_size (int) : the maximun results for page, by default is five [max is 50]

        output:
            request (dict) : a page of search
        """
        if DEBUG == True:
            print(f"(search_track) Query : {query}")

        argum = None
        metadata = str([query, type_filter, from_channel, results_size])
        if USES_API_CACHE == True:
            try:
                with open(r"cache/search.cache", "r") as local:
                    argum = local.readline().strip()
            except FileNotFoundError:
                print("(search_track) [ERROR] file not found. using api instead")

        if (argum == metadata):
            if DEBUG == True:
                print("(search_track) data location: local cache", end="\n\n")
            
            with open(r"cache/search.cache", "r") as local:
                local.readline()
                content = json.load(local)

            return content

        else:
            if DEBUG == True:
                print("(search_track) data location: API request", end="\n\n")

            if type_filter == "music":
                query += ' "topic"'
                type_filter = None

            request = request_one = self.API.search().list(
                part = "snippet",
                q = query,
                type = type_filter,
                channelId = from_channel,
                maxResults = results_size
            ).execute()

        # save cache
        with open(r"cache/search.cache", "w") as local:
            local.write(metadata + "\n")
            json.dump(request_one, local)

        return request