#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

"""
    Useful Links:
        1. https://www.programmersought.com/article/13205830225/ (nssm, service manager in windows)
        2. https://htmlpreview.github.io/?https://github.com/pyinstaller/pyinstaller/blob/v2.0/doc/Manual.html#a-note-on-using-upx
        3. https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html
        4. https://build-system.fman.io/
        5. https://heartbeat.fritz.ai/packaging-and-shipping-python-apps-for-the-desktop-a418489b854
    """
"""
Desktop applications are normally distributed by means of an installer. 
On Windows, this would be an executable called TutorialSetup.exe.
 On Mac, mountable disk images such as Tutorial.dmg are commonly used. 
On Linux, .deb files are common on Ubuntu, .rpm on Fedora / CentOS, and .pkg.tar.xz on Arch.
"""

cmd = r"""pyinstaller --noconfirm --onedir --windowed --name "Oncher" --upx-dir "I:/OpenSourceProjects/py-track/release/upx-3.96-win64" --log-level "DEBUG" --add-data "I:/FivverProjects/ONCHER-APP/templates;templates/" --add-data "I:/FivverProjects/ONCHER-APP/static;static/" --add-data "I:/FivverProjects/ONCHER-APP/database_schema;database_schema/" --paths "I:/FivverProjects/ONCHER-APP/venv/Lib/site-packages"  "I:/FivverProjects/ONCHER-APP/app.py" """.rstrip().lstrip()

# flake8 - skip PEP [E402, ]
