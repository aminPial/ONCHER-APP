from secrets import token_urlsafe

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

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
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@oncher_app.route('/favicon.ico')
def favicon_ico():
    return ""


from routers import *

database_cluster.create_all()
#
if __name__ == '__main__':
    database_cluster.create_all()
    socket_io.run(oncher_app, port=5000, debug=True)
