#Python_version : 3.13.5
#Pip_version : 25.1.1
#OS: Debian GNU/Linux 13 (Trixie)
#This script is not officially support by Google

import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_authenticated_service(token_path:str, client_secret_path:str = None) -> build:
    """
    Use or create the token json file to use the Oauth2 credentials with the api

    inputs:
        token_path (str) : path to open or save the token to access with the api
        client_secret_path (str|None) : path to the client secret json from the google cloud api, only necesary to create the token

    outputs:
        build (funtion) : build to use the youtube api v3

    @create by Gemini "Fast" (Google)
    """
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

youtube = get_authenticated_service("debug/token.json")

print("Autenticación exitosa. Ya puedes manipular tus playlists.")

request = youtube.videos().list(
        part="snippet",
        id="3X9F3FplWkM"
)

data = request.execute()

print(data)