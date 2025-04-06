from flask import Blueprint, request, jsonify, make_response
from app.models.UserModel import User
from app import db
from app.schema.UserSchema import UserSchemaRegister, UserSchemaLogin
from marshmallow import ValidationError
from app.service.AuthService import generate_tokens_and_create_cookie, refresh_access_token_and_update_cookie, try_parse_token_user_id, clear_auth_cookies
from sqlalchemy.exc import DatabaseError

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

  new_user = User(username=username, email=email)
  new_user.set_password(password)

  db.session.add(new_user)
  
  try:
    db.session.commit()
  except DatabaseError as e:
    return '', 500

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

@auth_bp.route("/auth/logout", methods=["GET"])
def logout():
  response = make_response('', 200)
  clear_auth_cookies(response)
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