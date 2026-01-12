#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Google


import os, json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# --- other data
NUMS = [str(i) for i in range(10)]


# --- contants
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
DEBUG = True
USES_API_CACHE = False
TOKEN_PATH = "debug/token.json"
CLIENT_SECRET_PATH = "debug/client_secret.apps.googleusercontent.com.json"

if os.path.exists(r"cache") == False:
    os.makedirs("cache")


class Youtube():
    def __init__ (self, token_path:str = TOKEN_PATH, client_secret_path:str = CLIENT_SECRET_PATH):
        """
        use or create the token json file to use the Oauth2 credentials with the api

        inputs:
            token_path (str) : path to open or save the token to access with the api
            client_secret_path (str|None) : path to the client secret json from the google cloud api, only necesary to create the token

        outputs:
            YOUTUBE (variable) : build to use the youtube api v3

        @with the help of Gemini "Fast" (Google)
        """
        flow = None
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if client_secret_path != None:
                    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print("the path of client_secret json is requiered to create the token.")
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        self.API = build('youtube', 'v3', credentials=creds)
        del flow
        del creds

        if DEBUG:
            print("login... ok")

        
    def get_video_info(self, ID:str) -> dict:
        """
        get basic info from a video using its id

        input:
            ID (str) : id of the video to get the info

        output:
            request [dict] : data from youtube api services
        """
        request = self.API.videos().list(
            id = ID,
            part = ["contentDetails", "snippet"]
            ).execute()
        
        del request["kind"]
        del request["etag"]

        # format the duration data
        time = []

        for x in request["items"][0]["contentDetails"]["duration"]:
            if x == "H" or x == "M":
                time.append(":")
            elif x in NUMS:
                time.append(x)
            
        duration = "".join(time)

        request["items"][0]["contentDetails"]["duration"] = duration

        return request

    def get_playlist_info(self, ID:str) -> dict:
            """
            get basic info from a playlist using its id

            input:
                ID (str) : id of the video to get the info

            output:
                request [dict] : data from youtube api services
            """

            # develop process
            if DEBUG == True:
                print(f"(get_playlist_info) playlist ID : {ID}")

            argum = None
            if USES_API_CACHE == True:
                try:
                    with open("cache/playlist.cache", "r") as local:
                        argum = local.readline().strip()
                except FileNotFoundError:
                    pass


            if (argum == ID):
                if DEBUG:
                    print("(get_playlist_info) data location: local cache", end="\n\n")
                
                with open("cache/playlist.cache", "r") as local:
                    local.readline()
                    content = json.load(local)

                return content

            else:
                if DEBUG:
                    print("(get_playlist_info) data location: API request", end="\n\n")

                request_one = self.API.playlists().list(
                    id = ID,
                    part = ["contentDetails", "snippet"]
                    ).execute()

                request_two = self.API.playlistItems().list(
                    playlistId = ID,
                    part = ["contentDetails"],
                    maxResults = 50
                    ).execute()

                tracks = []

                for iterator in request_two["items"]:
                    tracks.append(iterator["contentDetails"]["videoId"])

                request_one["tracks"] = tracks

                # save cache
                with open("cache/playlist.cache", "w") as local:
                    local.write(ID + "\n")
                    json.dump(request_one, local)

                return request_one



# --- Test
YT = Youtube()

#OLAK5uy_lZ_sOzsE6zU262uuuaPb-vVJJYcbs-b4I

a = YT.get_playlist_info("OLAK5uy_lZ_sOzsE6zU262uuuaPb-vVJJYcbs-b4I")

print("\n")

for i in a.keys():
    print(i, end="\n")
    print(a[i], end="\n\n")