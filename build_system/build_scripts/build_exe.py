#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

"""
For building Oncher App deliverable .exe, .dmg and .pkg.tar.xz files
"""

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
"""
# see https://upx.github.io/
# ! important: also check for upx platform specific build, like as i have x64 bit so win64
"""

import os
import shutil
import sys
from tqdm import tqdm
from time import time, sleep
import platform

"""
# STEPS 
    0. 
    1. 
"""

__build__ = 'WINDOWS-10'  # WINDOWS-7, WINDOWS-8, MacOS Sierra


def get_size(start_path='.'):
    # for files
    if os.path.isfile(start_path):
        return round(os.path.getsize(start_path) / (1024 * 1024), 2)
    # for folders
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return round(total_size / (1024 * 1024), 2)


def get_deep_size_analysis(root_path=os.path.abspath('..')):
    # print each file and folders size (only root)
    for file_folder in os.listdir(root_path):
        print("\t [ {} ] = {} M.B".format(file_folder, get_size(os.path.abspath(
            os.path.join(root_path, file_folder)))))


# 0. copy necessary files and folders to a temp folder
def copy_necessary_files_and_folders():
    temporary_folder = os.path.abspath(os.path.join(sys.path[0], '../temp'))
    source_folder = os.path.abspath('../..')

    if os.path.exists(temporary_folder):
        shutil.rmtree(temporary_folder)
    os.makedirs(temporary_folder)
    # files and folders to include
    files = [
        # scripts
        'app.py'
    ]
    folders = [
        # scripts
        'api',
        # assets
        'static',
        'templates',
        'db_file'
    ]
    print("[+++] Copying files & folders from {} to {}".format(source_folder, temporary_folder))

    for file in tqdm(files):
        shutil.copy(src=os.path.join(source_folder, file), dst=os.path.join(temporary_folder, file))
    for folder in tqdm(folders):
        shutil.copytree(src=os.path.join(source_folder, folder), dst=os.path.join(temporary_folder, folder))

    print("[+++] After coping files and folder - size: {} M.B".format(get_size(temporary_folder)))
    get_deep_size_analysis(temporary_folder)

    # if __build__ != "WINDOWS-10":
    #     # this is for 'cef_hook' for windows 7,8 builds as 'edgehtml' doesn't work for Windows 7,8
    #     # edgehtml only works for Windows 10 with
    #     files_and_folders.append('hook')
    # also beware of MACOS

    # clear db folder
    db_folder_path = os.path.abspath(os.path.join(temporary_folder, 'db_file'))
    shutil.rmtree(db_folder_path)

    # clean the "previously debugged" static files
    static_sub_folders_to_clear = ['cache',  # pdfs parsed images
                                   'files',  # pdf,ppt itself
                                   'flashcards',  # flashcard images
                                   # 'pickles',
                                   'screenshots'
                                   ]
    for sub_folder in tqdm(static_sub_folders_to_clear):
        folder_path = os.path.abspath(os.path.join(temporary_folder, 'static', sub_folder))
        shutil.rmtree(folder_path)

    print("[+++] After clearing unused files - size: {} M.B".format(get_size(temporary_folder)))
    get_deep_size_analysis(temporary_folder)


# 1. flake8 code-linting phase
def flake8_linting_phase():
    pass


# 2. pytest phase
def pytest_testing_phase():
    pass


# 3. building with pyinstaller
def building_with_pyinstaller():
    print("[+++] Building package via Pyinstaller..")
    # check config in pyinstaller_config_builder CONFIG section
    from pyinstaller_config_builder import get_pyinstaller_buffer

    try:
        os.system(get_pyinstaller_buffer())
        sleep(5)
        os.chdir(r"I:\FivverProjects\ONCHER-APP\build_system\build_output\dist\Oncher")
        os.startfile(r"I:\FivverProjects\ONCHER-APP\build_system\build_output\dist\Oncher\Oncher.exe")
    except Exception as e:
        print("Failed to build .exe due to {}".format(e))


if __name__ == '__main__':
    start = time()

    print("\n{}Running <ATIKE> Build System on {} - {} - {}\n{}Python Engine: {} - {}\n".format(
        "\t" * 8,
        platform.system(),
        platform.machine(),
        platform.processor(),
        "\t" * 15,
        platform.python_implementation(),
        platform.python_version()
    ))

    copy_necessary_files_and_folders()
    flake8_linting_phase()
    pytest_testing_phase()
    building_with_pyinstaller()

    print("Build Folder Size [with UPX]: {} M.B".format(
        get_size(r"I:\FivverProjects\ONCHER-APP\build_system\build_output\dist\Oncher")))
    print("[+++] Building System took {} minutes to build".format(round((time() - start) / 60), 2))

    from inno_config_builder import get_inno_config
    get_inno_config()