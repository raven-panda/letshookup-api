# Import all controllers here
from app.controllers.AuthController import auth_bp
from app import app

app.register_blueprint(auth_bp, url_prefix='/api')