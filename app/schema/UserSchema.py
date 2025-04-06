from marshmallow import Schema, fields, validates_schema, ValidationError
from app.models.UserModel import User

class UserSchemaRegister(Schema):
  username = fields.String(required=True)
  email = fields.String(required=True)
  password = fields.String(required=True)
  password_verify = fields.String(required=True, data_key="passwordVerify")

  @validates_schema
  def validate_passwords_match(self, data, **kwargs):
    errors = {}

    if data.get("password") != data.get("password_verify"):
      errors["password_verify"] = ["Passwords do not match"]

    if User.query.filter_by(username=data.get("username")).first():
      errors["username"] = ["Username already used"]

    # Vérifie si l'email est déjà utilisé
    if User.query.filter_by(email=data.get("email")).first():
      errors["email"] = ["Account already exists"]

    if errors:
      raise ValidationError(errors)
    
class UserSchemaLogin(Schema):
  email = fields.String(required=True)
  password = fields.String(required=True)