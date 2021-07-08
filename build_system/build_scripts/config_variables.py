def get_build_name():
    from string import ascii_lowercase
    from random import randint
    build_name = ""
    build_name_length = 5
    for _ in range(build_name_length):
        build_name += ascii_lowercase[randint(0, 25)]
    return build_name


# ======================================= CONFIGS ==========================================

_APP_NAME = "Oncher"
# you need to change version name here for inno and server(most important)
_VERSION_NAME = "0.0.2"  # major: 0 , minor: 0, patch: 1 build_name: 5 length
_APP_ICON_PATH = '10_BUi_icon.ico'
_APP_ENTRY_SCRIPT_PATH = 'app.py'

_IS_WINDOWED = False  # false means console
_IS_ONE_DIR = True  # false means onefile
_LOG_LEVEL = 'DEBUG'  # INFO, ERROR, CRITICAL

_ASSETS_FILES = [
    'assets.zip'
]

_BUILD_FOLDER_PATH = "build"
_DIST_FOLDER_PATH = "dist"
_UPX_DIRECTORY = 'upx-3.96-win64'

_OPTIMIZE_LEVEL = 2  # 0 - no optimization | 1- basic optimization | 2- 1 + docstring optimization

# _HOOK_DIRECTORY = 'hook'
# additional potential options => exclude_module, hidden imports
