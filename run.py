import os
import eventlet

if os.environ.get("FLASK_ENV", "development") != "production":
	from dotenv import load_dotenv
	load_dotenv()

eventlet.monkey_patch()

from app import app, socketio

port = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
	socketio.run(app, host='0.0.0.0', port=port, debug=os.environ.get("FLASK_DEBUG") == 'True')