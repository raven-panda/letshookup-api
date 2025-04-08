import jwt
import datetime
import os
from flask import current_app, Response

def generate_access_token(user_id: str):
  """
  Encodes a JWT token with 15 minute expiration
  Uses the given user_id
  """
  access_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  return access_token

def generate_tokens(user_id: str):
  """
  Encodes two JWT token : an access token with 15 minute expiration and a refresh token with 7 days expiration.
  Uses the given user_id

  Returns
  -------
  tuple[str, str]
    Tuple of JWT tokens (access_token, refresh_token)
  """
  refresh_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  access_token = generate_access_token(user_id)

  return access_token, refresh_token

def create_accesstoken_cookie(response: Response, token: str):
  """
  Set access_token cookie with the given token as value

  Parameters
  -------
  response : Response
    The response you want to return, **Set-Cookie** access_token header will be added to it.
  token : str
    Access token to put in the cookie
  """
  response.set_cookie(
    'access_token',
    token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=900
  )

def create_refresh_cookie(response: Response, token: str):
  """
  Set refresh_token cookie with the given token as value

  Parameters
  -------
  response : Response
    The response you want to return, **Set-Cookie** refresh_token header will be added to it.
  token : str
    Refresh token to put in the cookie
  """
  response.set_cookie(
    'refresh_token',
    token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=604800
  )

def create_token_cookies(response: Response, access_token: str, refresh_token: str):
  """
  Set refresh_token and access_token cookie with the given token as value

  Parameters
  -------
  response : Response
    The response you want to return, **Set-Cookie** refresh_token header will be added to it.
  access_token : str
    Refresh token to put in the cookie
  refresh_token : str
    Access token to put in the cookie
  """
  create_refresh_cookie(response, refresh_token)
  create_accesstoken_cookie(response, access_token)

def generate_tokens_and_create_cookie(response, user_id):
  access_token, refresh_token = generate_tokens(user_id)
  create_token_cookies(response, access_token, refresh_token)

def refresh_access_token_and_update_cookie(response, user_id):
  """
  Recreates access token with the given refresh token

  Parameters
  ----------
  response : Response
    The response you want to return, Set-Cookie headers will be added to it.
  user_id : str
    User ID parsed from original refresh token
  """
  access_token = generate_access_token(user_id)
  create_accesstoken_cookie(response, access_token)

def try_parse_token_user_id(token: str):
  """
  Try to parse the user ID from the given token

  Parameters
  ----------
  token : str
    Token where to parse the ID


  Returns
  ----------
  str | None
    The parsed user ID
  """
  if not token:
    return None

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload['sub']
  except jwt.ExpiredSignatureError:
    return None
  except jwt.InvalidTokenError:
    return None
  
  return user_id

def clear_auth_cookies(response: Response):
  """
  Try to parse the user ID from the given token

  Parameters
  ----------
  response: Response
    The response you want to return, Set-Cookie headers will be added to it with expired cookies.
  """
  response.set_cookie('refresh_token', '', expires=0)
  response.set_cookie('access_token', '', expires=0)