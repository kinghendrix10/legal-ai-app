# app/__init__.py

from flask import Flask
from flask_socketio import SocketIO
from config import Config

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    socketio.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app