from json.decoder import JSONDecodeError
from django.db import models
from .models import SpotifyToken 
from datetime import timedelta
from django.utils import timezone
from .credentials import client_secret, client_id, redirect_uri
from requests import post, get, put

BASE_URL = "https://api.spotify.com/v1/me/"

def get_user_tokens(session_id):
    queryset = SpotifyToken.objects.filter(user=session_id)

    if queryset.exists():
        return queryset[0]
    else:
        return None

def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])

    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token, expires_in=expires_in, refresh_token=refresh_token, token_type=token_type)

        tokens.save()

def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    error = ""
    if tokens:
        
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            print("ITSREFRESHINGGGG")
            error = refresh_spotify_token(session_id)

        return True, error

    return False, error

def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token
    print('WAS ABLE TO GET REFRESH TOKENS FROM DATABASE?')
    try:
        response = post('https://accounts.spotify.com/authorize', data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
        }).json()
        print(response)
    except JSONDecodeError as e:
        return{ "JSON Decode Error": "You Caused a JSONDecodeError because the post request to get the new access token came back with no repsonse. \n This is the Error: " + str(e)}
        print("This is the response from your post request using refresh token: actually idk")
    except Exception as e:
        print("Unclear of what the error is: " + e.__str__())
    
    print('Was able to good try except block?')

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    # refresh_token = response.get('refresh_token') # We dont get new refresh token -> This will cause error by putting "None"

    update_or_create_user_tokens(session_id,access_token, token_type, expires_in, refresh_token)


def execute_spotify_api_request(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tokens.access_token}

    if post_:
        post(BASE_URL + endpoint, headers=headers)

    if put_:
        put(BASE_URL + endpoint, headers=headers)

    response = get(BASE_URL + endpoint, {}, headers=headers)

    try:
        return response.json()
    except:
        return{'Error': 'Issue with Request (Most likely using other types of spotify applications than Web Application Version.)'}

def play_song(session_id):
    return execute_spotify_api_request(session_id, "player/play", put_=True)

def pause_song(session_id):
    return execute_spotify_api_request(session_id, "player/pause", put_=True)

def skip_song(session_id):
    return execute_spotify_api_request(session_id, "player/next", post_=True)