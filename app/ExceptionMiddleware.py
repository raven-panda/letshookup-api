import traceback

from flask import jsonify, make_response
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException, Unauthorized, Forbidden

from app import app
from app.service.AuthService import clear_auth_cookies


# Catch all unhandled exceptions
@app.errorhandler(Exception)
def handle_generic_exception(e: Exception):
  app.logger.error(e)
  res = {"errors": ["Internal server error"]}

  print(app.config)
  if app.config.get('DEBUG'):
    res['trace'] = traceback.format_exception(e)

  return jsonify(res), 500

@app.errorhandler(ValidationError)
def handle_validation_error(e):
  app.logger.error(e)
  res = {"errors": e.messages}
  return jsonify(res), 400

@app.errorhandler(HTTPException)
def handle_http_exception(e: HTTPException):
  app.logger.error(e)
  res = {"errors": e.description}
  return jsonify(res), e.code

@app.errorhandler(Unauthorized)
def handle_auth_errors(e: Unauthorized ):
  app.logger.error(e)
  res = make_response('', e.code)
  clear_auth_cookies(res)

  return res

@app.errorhandler(Forbidden)
def handle_auth_errors(e: Forbidden):
  app.logger.error(e)
  return '', e.code