#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Google


import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# --- other data
NUMS = [str(i) for i in range(10)]


# --- contants
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
DEBUG = True
TOKEN_PATH = "debug/token.json"
CLIENT_SECRET_PATH = "debug/client_secret.apps.googleusercontent.com.json"


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
        get basic info from a video usign its id

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



# --- Test
YT = Youtube()