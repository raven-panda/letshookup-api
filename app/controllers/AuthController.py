import os
from flask import Blueprint, request, jsonify, make_response
from app.models.UserModel import User
from app import db
from app.schema.UserSchema import UserSchemaRegister, UserSchemaLogin
from marshmallow import ValidationError
from app.service.AuthService import generate_tokens
import jwt
import datetime
from flask import current_app

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
  schema = UserSchemaRegister()

  try:
    data = schema.load(request.json)
  except ValidationError as err:
    return jsonify({"errors": err.messages}), 400

  username = data.get("username")
  email = data.get("email")
  password = data.get("password")

  if not username or not password:
    return jsonify({"error": "Missing username or password"}), 400

  if User.query.filter_by(username=username).first():
    return jsonify({"error": "User already exists"}), 409

  new_user = User(username=username, email=email)
  new_user.set_password(password)

  db.session.add(new_user)
  db.session.commit()

  return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
  schema = UserSchemaLogin()

  try:
    data = schema.load(request.json)
  except ValidationError as err:
    return jsonify({"errors": err.messages}), 400
  
  email = data.get("email")
  password = data.get("password")

  user = User.query.filter_by(email=email).first()
  if user is None or not user.check_password(password):
    return jsonify({"error": "Invalid credentials"}), 401
  
  access_token, refresh_token = generate_tokens(user.id)

  userDto = { "id": user.id, "email": user.email }

  response = make_response(jsonify(userDto))
  
  # Ajouter le token dans un cookie HTTPOnly sécurisé
  response.set_cookie(
    'access_token',
    access_token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=900
  )

  response.set_cookie(
    'refresh_token',
    refresh_token,
    httponly=True,
    secure=os.getenv('ENABLE_HTTPS') is 'True',
    samesite='Strict',
    max_age=604800
  )

  return response

@auth_bp.get('/auth/refresh')
def refresh_auth_token():
  refresh_token = request.cookies.get('refresh_token')
  print(refresh_token)
  if not refresh_token:
    return jsonify({'message': 'Bad credentials'}), 401
  
  try:
    payload = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload['sub']
  except jwt.ExpiredSignatureError:
    return jsonify({'message': 'Refresh token expired'}), 401
  except jwt.InvalidTokenError:
    return jsonify({'message': 'Invalid token'}), 401
  
  new_access_token = jwt.encode({
    'sub': user_id,
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
  }, current_app.config['SECRET_KEY'], algorithm='HS256')

  response = make_response(jsonify({'message': 'Access token refreshed'}))
  response.set_cookie('access_token', new_access_token, httponly=True, secure=os.getenv('ENABLE_HTTPS') is 'True', samesite='Strict', max_age=900)

  return response