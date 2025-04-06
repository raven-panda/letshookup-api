from flask_socketio import emit, join_room, leave_room
from app import socketio
from flask import request, current_app
import jwt
from app.service.AuthService import try_parse_token_user_id

@socketio.on('connect', namespace='/chat')
def handle_connect():
  token = request.cookies.get('access_token')
  if not token:
    return False

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    user_id = payload.get('sub')
  except Exception as e:
    print('Invalid token:', e)
    return False

  join_room(user_id)
  print(f"User {user_id} joined room")

@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
  token = request.cookies.get('access_token')
  if not token:
    return False

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    user_id = payload.get('sub')
  except Exception as e:
    print('Invalid token:', e)
    return False

  leave_room(user_id)

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
  token = request.cookies.get('refresh_token')
  sender_id = try_parse_token_user_id(token)
  recipient_id = data.get("to")
  message = data.get("message")
  
  if not recipient_id or not message:
    return
  
  payload = {
    "from": sender_id,
    "message": message
  }

  emit('receive_message', payload, room=recipient_id)

  emit('receive_message', payload, room=sender_id)
