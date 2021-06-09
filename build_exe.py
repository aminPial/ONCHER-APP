import os
import sys
import shutil


cmd = r"""pyinstaller --noconfirm --onedir --windowed --name "Oncher" --upx-dir "I:/OpenSourceProjects/py-track/release/upx-3.96-win64" --log-level "DEBUG" --add-data "I:/FivverProjects/ONCHER-APP/templates;templates/" --add-data "I:/FivverProjects/ONCHER-APP/static;static/" --add-data "I:/FivverProjects/ONCHER-APP/database;database/" --paths "I:/FivverProjects/ONCHER-APP/venv/Lib/site-packages"  "I:/FivverProjects/ONCHER-APP/app.py" """.rstrip().lstrip()

