import os
from flask import Blueprint, request, jsonify, make_response
from app.models.UserModel import User
from app import db
from app.schema.UserSchema import UserSchemaRegister, UserSchemaLogin
from marshmallow import ValidationError
from app.service.AuthService import generate_tokens_and_create_cookie, refresh_access_token_and_update_cookie, try_parse_token_user_id
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

  response = make_response('', 201)
  generate_tokens_and_create_cookie(response, new_user.id)

  return response

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

  response = make_response('')
  generate_tokens_and_create_cookie(response, user.id)

  return response

@auth_bp.get('/auth/refresh')
def refresh_auth_token():
  refresh_token = request.cookies.get('refresh_token')
  user_id = try_parse_token_user_id(refresh_token)

  if not user_id:
    return '', 401

  response = make_response('')
  refresh_access_token_and_update_cookie(response, user_id)

  return response