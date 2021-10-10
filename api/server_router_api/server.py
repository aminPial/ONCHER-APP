#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021


RELEASE_BUILD = True  # THIS IS IMPORTANT
_VERSION_NAME = "0.0.5"  # change when building for a new release(if changes internal files)

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
import threading

# logger.debug("Process ID: {} - Thread - {}".format(os.getpid(), threading.current_thread()))
import shutil

# for release build only [9 folders in static, remember that]
APP_DATA_FOLDER_PATH = os.path.join(os.environ['APPDATA'], "Oncher")


# print("App data folder for Oncher is {}".format(APP_DATA_FOLDER_PATH))
def manage_app_data_folder(full_clean: bool = False):
    # always run: 1
    shutil.copy(src=os.path.abspath(os.path.join('.', 'assets.zip')), dst=APP_DATA_FOLDER_PATH)

    if not full_clean:
        # make a tmp folder to extract assets
        tmp_extract_dir = os.path.join(APP_DATA_FOLDER_PATH, 'tmp_extract_dir')
        if os.path.exists(tmp_extract_dir):
            shutil.rmtree(tmp_extract_dir)
        os.makedirs(tmp_extract_dir)

    # copy the asset zip from the Programs dir to AppData if full clean else AppData/emp_extract_dir
    tmp = 'tmp_extract_dir'
    shutil.unpack_archive(os.path.join(APP_DATA_FOLDER_PATH, 'assets.zip'),  # from
                          os.path.join(APP_DATA_FOLDER_PATH, '' if full_clean else tmp),  # to
                          'zip')

    if not full_clean:

        # dev-end folders
        # cache (loading screen gif/image), templates, static/js,css,images,sounds
        # now remove the previous folders that will be re-written from fresh assets
        shutil.rmtree(os.path.join(APP_DATA_FOLDER_PATH, 'cache'))
        shutil.copytree(src=os.path.join(APP_DATA_FOLDER_PATH, tmp, 'cache'),
                        dst=os.path.join(APP_DATA_FOLDER_PATH, 'cache'))

        shutil.rmtree(os.path.join(APP_DATA_FOLDER_PATH, 'templates'))
        shutil.copytree(src=os.path.join(APP_DATA_FOLDER_PATH, tmp, 'templates'),
                        dst=os.path.join(APP_DATA_FOLDER_PATH, 'templates'))

        for static_folder in ['css', 'js', 'sounds', 'images']:
            shutil.rmtree(os.path.join(APP_DATA_FOLDER_PATH, 'static', static_folder))
            shutil.copytree(src=os.path.join(APP_DATA_FOLDER_PATH, tmp, 'static', static_folder),
                            dst=os.path.join(APP_DATA_FOLDER_PATH, 'static', static_folder))

    if not full_clean:
        shutil.rmtree(os.path.join(APP_DATA_FOLDER_PATH, 'tmp_extract_dir'))

    # always run: 2
    os.remove(os.path.join(APP_DATA_FOLDER_PATH, 'assets.zip'))
    logger.warning("After unpacking the folder lists are: ".format([
        folder for folder in os.listdir(APP_DATA_FOLDER_PATH) if os.path.isdir(folder)
    ]))

    print("this is first run. so writing pickle")
    # we can only write to APPDATA folder
    import pickle
    with open(os.path.join(APP_DATA_FOLDER_PATH, 'version.pickle'), 'wb') as han:
        pickle.dump({'version': _VERSION_NAME}, han, protocol=pickle.HIGHEST_PROTOCOL)


if RELEASE_BUILD:
    """
        # case 1: Oncher App folder in APPDATA doesn't exist (simple, full_clean)
        # case 2: Oncher App exists but pickle doesn't exist (complex, half-clean, clean only dev-end folders like css,js)
        #         full_clean = False == half_clean
        # case 3: normal run (don't do anything)
    """
    if not os.path.exists(APP_DATA_FOLDER_PATH):
        logger.warning("Inside Release build folder manager")
        os.makedirs(APP_DATA_FOLDER_PATH)
        manage_app_data_folder(full_clean=True)
    else:
        import pickle

        with open(os.path.join(APP_DATA_FOLDER_PATH, 'version.pickle'), 'rb') as handle:
            version = pickle.load(handle)['version']
            if version != _VERSION_NAME:
                print("Half clean...")
                manage_app_data_folder(full_clean=False)
            else:
                print("normal run")

oncher_app = Flask(__name__,
                   static_folder=os.path.join(os.environ['APPDATA'], "Oncher", "static")
                   if RELEASE_BUILD else os.path.abspath(os.path.join('.', 'static')),
                   template_folder=os.path.join(os.environ['APPDATA'], "Oncher", "templates")
                   if RELEASE_BUILD else os.path.abspath(os.path.join('.', 'templates')))

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
