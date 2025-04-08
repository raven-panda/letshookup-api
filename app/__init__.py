# Initialize app here
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO

def init_components():
  from app import models, controllers, sockets, ExceptionMiddleware

flask_env = os.getenv("FLASK_ENV")
config_name = "app.config.DevConfig" if flask_env == "development" else "app.config.ProductionConfig" if flask_env == "production" else "app.config.TestConfig" if flask_env == "test" else None

if config_name is None:
  message = f"'FLASK_ENV' doesn't match expected values : development, production, test. Got {flask_env} instead."
  raise Exception(message)

app = Flask(__name__)
app.config.from_object(config_name)

cors = CORS(app, supports_credentials=True, origins = os.getenv("CORS_ACCEPTED_URI").split(','))

db = SQLAlchemy(app)

socketio = SocketIO(cors_allowed_origins=os.getenv("CORS_ACCEPTED_URI").split(','))
socketio.init_app(app)

init_components()

migrate = Migrate(app, db)

with app.app_context():
  db.create_all()