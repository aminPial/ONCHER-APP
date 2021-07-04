#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

# see https://pyinstaller.readthedocs.io/en/stable/usage.html#general-options

import os
import shutil


# ======================================= pyinstaller command BUILDER ==========================================

# re-shape configs (some of them if necessary)
def get_pyinstaller_buffer():
    from config_variables import _APP_ICON_PATH, _APP_ENTRY_SCRIPT_PATH, \
        _ASSETS_FOLDER, _BUILD_FOLDER_PATH, _DIST_FOLDER_PATH, _UPX_DIRECTORY, \
        _IS_WINDOWED, _IS_ONE_DIR, _APP_NAME, _LOG_LEVEL

    _APP_ICON_PATH = os.path.abspath(os.path.join('..', 'temp', 'static', 'images', _APP_ICON_PATH))
    _APP_ENTRY_SCRIPT_PATH = os.path.abspath(os.path.join('..', 'temp', _APP_ENTRY_SCRIPT_PATH))

    _ASSETS_FOLDER = [
        os.path.abspath(os.path.join('..', 'temp', folder_name))
        for folder_name in _ASSETS_FOLDER
    ]

    _BUILD_FOLDER_PATH = os.path.abspath(os.path.join("..", "build_output", _BUILD_FOLDER_PATH))
    _DIST_FOLDER_PATH = os.path.abspath(os.path.join("..", "build_output", _DIST_FOLDER_PATH))
    _UPX_DIRECTORY = os.path.abspath(os.path.join('..', 'upxs', _UPX_DIRECTORY))

    # switches will be added like --{switch_name}
    switches = [
        "--clean",
        "--noconfirm",
        '--onedir' if _IS_ONE_DIR else '--onefile',
        '--windowed' if _IS_WINDOWED else '--console'
    ]
    _switch_buffer = " ".join(list(map(str, switches)))

    # --onedir --console
    key_value_config_list = [
                                {
                                    "optionDest": "name",
                                    "value": _APP_NAME
                                },
                                {
                                    "optionDest": "log-level",
                                    "value": _LOG_LEVEL
                                }
                                # {
                                #     "optionDest": "strip",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "noupx",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "uac_admin",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "uac_uiaccess",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "win_private_assemblies",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "win_no_prefer_redirects",
                                #     "value": false
                                # },
                                # {
                                #     "optionDest": "bootloader_ignore_signals",
                                #     "value": false
                                # }
                            ] + [
                                {
                                    "optionDest": "add-data",
                                    "value": """ "{source_full_path};{destination_folder_name_only}/" """.format(
                                        # source (from where it will be copied)
                                        source_full_path=folder_full_path,
                                        # destination folder to put
                                        destination_folder_name_only=
                                        folder_full_path.split("\\")[-1])  # this can be buggy in other platform
                                }
                                for folder_full_path in _ASSETS_FOLDER
                            ]

    key_value_config_buffer = " ".join(map(str,
                                           ['--{key} {value}'.format(key=pair["optionDest"],
                                                                     value=pair['value'])
                                            for pair in key_value_config_list
                                            ])) + \
                              """ --upx-dir "{}"  """.format(_UPX_DIRECTORY) + \
                              """ --icon "{}" """.format(_APP_ICON_PATH) + \
                              """ --distpath "{}" """.format(_DIST_FOLDER_PATH) + \
                              """ --workpath "{}" """.format(_BUILD_FOLDER_PATH)

    _pyinstaller_execute_buffer = "pyinstaller " + _switch_buffer + " " + key_value_config_buffer \
                                  + " " + _APP_ENTRY_SCRIPT_PATH
    print(_pyinstaller_execute_buffer)

    # clean build and dest folder before exec
    if os.path.exists(_BUILD_FOLDER_PATH):
        shutil.rmtree(_BUILD_FOLDER_PATH)
    os.makedirs(_BUILD_FOLDER_PATH)

    if os.path.exists(_DIST_FOLDER_PATH):
        shutil.rmtree(_DIST_FOLDER_PATH)
    os.makedirs(_DIST_FOLDER_PATH)

    # remove spec file
    # spec_file_path = os.path.abspath('Oncher.spec')
    # if os.path.exists(spec_file_path):
    #     os.remove(spec_file_path)

    # see for optimizations flag
    # https://pyinstaller.readthedocs.io/en/stable/usage.html#running-pyinstaller-with-python-optimizations
    # use if -OO flag

    return _pyinstaller_execute_buffer
