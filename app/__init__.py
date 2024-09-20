# app/__init__.py

from flask import Flask, session
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    socketio.init_app(app)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app