import jwt
import datetime
import os
from flask import current_app, Response

def generate_access_token(user_id):
  access_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  return access_token

def generate_tokens(user_id):
  refresh_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  access_token = generate_access_token(user_id)

  return access_token, refresh_token

def create_accesstoken_cookie(response: Response, token: str):
  response.set_cookie(
    'access_token',
    token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=900
  )

def create_refresh_cookie(response: Response, token: str):
  response.set_cookie(
    'refresh_token',
    token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=604800
  )

def create_token_cookies(response: Response, access_token: str, refresh_token: str):
  create_refresh_cookie(response, refresh_token)
  create_accesstoken_cookie(response, access_token)

def generate_tokens_and_create_cookie(response, user_id):
  access_token, refresh_token = generate_tokens(user_id)
  create_token_cookies(response, access_token, refresh_token)

def refresh_access_token_and_update_cookie(response, user_id):
  access_token = generate_access_token(user_id)
  create_accesstoken_cookie(response, access_token)

def try_parse_token_user_id(refresh_token):
  if not refresh_token:
    return None

  try:
    payload = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload['sub']
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError:
    return None
  
  return user_id

def clear_auth_cookies(response: Response):
  response.set_cookie('refresh_token', '', expires=0)
  response.set_cookie('access_token', '', expires=0)