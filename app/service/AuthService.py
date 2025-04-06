import jwt
import datetime
from flask import current_app

def generate_tokens(user_id):
  access_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  refresh_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  return access_token, refresh_token