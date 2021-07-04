# ======================================= CONFIGS ==========================================

_APP_NAME = "Oncher"
_VERSION_NAME = "0.0.1"  # major: 0 , minor: 0, patch: 1
_APP_ICON_PATH = '10_BUi_icon.ico'
_APP_ENTRY_SCRIPT_PATH = 'app.py'

_IS_WINDOWED = True  # false means console
_IS_ONE_DIR = True  # false means onefile
_LOG_LEVEL = 'DEBUG'  # INFO, ERROR, CRITICAL

_ASSETS_FOLDER = [
    'static',
    'templates'
]

_BUILD_FOLDER_PATH = "build"
_DIST_FOLDER_PATH = "dist"
_UPX_DIRECTORY = 'upx-3.96-win64'

_OPTIMIZE_LEVEL = 2  # 0 - no optimization | 1- basic optimization | 2- 1 + docstring optimization

# _HOOK_DIRECTORY = 'hook'
# additional potential options => exclude_module, hidden imports
