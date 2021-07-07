#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

RELEASE_BUILD = False  # THIS IS IMPORTANT

import logging
import coloredlogs

# setting the logs
logger = logging.getLogger('oncher_app')
LEVEL_STYLE = {'spam': {'color': 'green', 'faint': True},
               'debug': {'color': 'magenta'},
               'verbose': {'color': 'blue'},
               'info': {'color': 'cyan'},
               'notice': {'color': 'magenta'},
               'warning': {'color': 'yellow'},
               'success': {'color': 'green', 'bold': True},
               'error': {'color': 'red'},
               'critical': {'color': 'red', 'bold': True}}
coloredlogs.install(level='DEBUG',  # 'DEBUG'
                    logger=logger,
                    fmt='%(asctime)s %(module)s.py->%(funcName)s()->Line %(lineno)d %(levelname)s %(message)s',
                    level_styles=LEVEL_STYLE)

from secrets import token_urlsafe

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os
import shutil

# for release build only [9 folders in static, remember that]
APP_DATA_FOLDER_PATH = os.path.join(os.environ['APPDATA'], "Oncher")
print("App data folder for Oncher is {}".format(APP_DATA_FOLDER_PATH))

if RELEASE_BUILD:
    if not os.path.exists(APP_DATA_FOLDER_PATH):
        os.makedirs(APP_DATA_FOLDER_PATH)

    logger.warning("folder tree {}".format(os.listdir()))
    if len(os.listdir(APP_DATA_FOLDER_PATH)) == 0:
        shutil.copy(src=os.path.abspath(os.path.join('.', 'assets.zip')), dst=APP_DATA_FOLDER_PATH)
        shutil.unpack_archive(os.path.join(APP_DATA_FOLDER_PATH, 'assets.zip'),
                              APP_DATA_FOLDER_PATH, 'zip')
        os.remove(os.path.join(APP_DATA_FOLDER_PATH, 'assets.zip'))

oncher_app = Flask(__name__,
                   static_folder=os.path.join(os.environ['APPDATA'], "Oncher", "static")
                   if RELEASE_BUILD else os.path.abspath(os.path.join('.', 'static')),
                   template_folder=os.path.abspath(os.path.join('.', 'templates')))

logger.info("Called From {} -  Root Path {}".format(__name__, os.path.abspath('')))

# three slashes for relative paths, four for absolute paths.
_SQL_DB_PATH = r'sqlite:///{database_path}'.format(
    database_path=os.path.abspath(os.path.join('db_file', 'cluster.sqlite3')) if not RELEASE_BUILD else
    os.path.join(os.environ['APPDATA'], "Oncher", 'db_file', 'cluster.sqlite3')
)
logger.warning("SQL DB PATH: {}".format(_SQL_DB_PATH))

config = {
    'SECRET_KEY': token_urlsafe(500),
    'SQLALCHEMY_DATABASE_URI': _SQL_DB_PATH,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    'SEND_FILE_MAX_AGE_DEFAULT': 0
}
oncher_app.config.update(config)
socket_io = SocketIO(oncher_app, cors_allowed_origins='*')
database_cluster = SQLAlchemy(oncher_app)


# no cache setup
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


from api.server_router_api.routers import *

# st = time.time()
database_cluster.create_all()
# print("took {} sec".format(time.time() - st))
# if __name__ == '__main__':
#     database_cluster.create_all()
#     socket_io.run(oncher_app, port=5000, debug=True)
