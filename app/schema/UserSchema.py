from marshmallow import Schema, fields, validates_schema, ValidationError

class UserSchemaRegister(Schema):
  username = fields.String(required=True)
  email = fields.String(required=True)
  password = fields.String(required=True)
  password_verify = fields.String(required=True, data_key="passwordVerify")

  @validates_schema
  def validate_passwords_match(self, data, **kwargs):
    if data.get("password") != data.get("password_verify"):
      raise ValidationError("Passwords do not match", field_name="password_verify")
    
class UserSchemaLogin(Schema):
  email = fields.String(required=True)
  password = fields.String(required=True)