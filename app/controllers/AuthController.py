from flask import Blueprint, request, jsonify, make_response
from app.models.UserModel import User
from app import db
from app.schema.UserSchema import UserSchemaRegister, UserSchemaLogin
from werkzeug.exceptions import Unauthorized, InternalServerError
from app.service.AuthService import generate_tokens_and_create_cookie, refresh_access_token_and_update_cookie, try_parse_token_user_id, clear_auth_cookies
from sqlalchemy.exc import DatabaseError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
  schema = UserSchemaRegister()

  data = schema.load(request.json)

  username = data.get("username")
  email = data.get("email")
  password = data.get("password")

  new_user = User(username=username, email=email)
  new_user.set_password(password)

  db.session.add(new_user)
  
  try:
    db.session.commit()
  except DatabaseError as e:
    raise InternalServerError()

  response = make_response('', 201)
  generate_tokens_and_create_cookie(response, new_user.id)

  return response

@auth_bp.route("/auth/login", methods=["POST"])
def login():
  schema = UserSchemaLogin()
  data = schema.load(request.json)
  
  email = data.get("email")
  password = data.get("password")

  user = User.query.filter_by(email=email).first()
  if user is None or not user.check_password(password):
    raise Unauthorized()

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
  access_token = request.cookies.get('access_token')

  # Comparing credentials between both tokens
  refresh_token_user_id = try_parse_token_user_id(refresh_token)
  access_token_user_id = try_parse_token_user_id(access_token)

  # Throw Unauthorized if user ID parsed from refresh token is null or if both IDs didn't match
  if not refresh_token_user_id or refresh_token_user_id != access_token_user_id:
    raise Unauthorized()

  response = make_response('')
  refresh_access_token_and_update_cookie(response, refresh_token_user_id)

  return response