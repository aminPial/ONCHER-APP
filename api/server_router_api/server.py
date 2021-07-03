#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

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
coloredlogs.install(level='DEBUG',
                    logger=logger,
                    fmt='%(asctime)s %(module)s.py->%(funcName)s()->Line %(lineno)d %(levelname)s %(message)s',
                    level_styles=LEVEL_STYLE)

from secrets import token_urlsafe

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os
import sys

root_path = os.path.join(sys.path[0])

oncher_app = Flask(__name__,
                   static_url_path='',
                   static_folder=os.path.join(root_path, 'static'),
                   template_folder=os.path.join(root_path, 'templates'))
logger.info("Root Path {}".format(root_path))

config = {
    'SECRET_KEY': token_urlsafe(500),
    'SQLALCHEMY_DATABASE_URI': r'sqlite:///{database_path}'.format(
        database_path=os.path.join(root_path, 'database_schema', 'cluster.sqlite3')
    ),
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
