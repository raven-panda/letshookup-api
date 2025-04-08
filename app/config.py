import os

class Config(object):
	"""
	Configuration base, for all environments.
	"""
	DEBUG = os.getenv('FLASK_DEBUG') == 'True'
	TESTING = False
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
	SECRET_KEY = os.getenv('SECRET_KEY')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	BOOTSTRAP_FONTAWESOME = True
	CSRF_ENABLED = True

class ProdConfig(Config):
	SQLALCHEMY_DATABASE_URI = 'mysql://user@localhost/foo'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(Config):
	DEBUG = os.getenv('FLASK_DEBUG') == 'True'

class TestConfig(Config):
	TESTING = True
	