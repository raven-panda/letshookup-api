from app import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
  id = db.Column(db.String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
  username = db.Column(db.String(64), unique=True, nullable=False)
  email = db.Column(db.String(200), unique=True, nullable=False)
  password_hash = db.Column(db.String(255), nullable=False)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)