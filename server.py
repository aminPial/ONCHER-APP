from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from secrets import token_urlsafe

oncher_app = Flask(__name__)

config = {
    'SECRET_KEY': token_urlsafe(500),
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///database/cluster.sqlite3',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    'SEND_FILE_MAX_AGE_DEFAULT': 0
}
oncher_app.config.update(config)
socket_io = SocketIO(oncher_app, cors_allowed_origins='*')
database_cluster = SQLAlchemy(oncher_app)
# CORS(oncher_app)


# # no cache
@oncher_app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


from routers import *
from models import *


# @oncher_app.route('/favicon.ico')
# def favicon_ico():
#     return ""


# if __name__ == '__main__':
#     database_cluster.create_all()
#     socket_io.run(oncher_app, port=5000, debug=True)
