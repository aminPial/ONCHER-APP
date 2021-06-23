from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

import pyautogui as p
from webview import create_window, start
# from webview.platforms.cef import settings  #
from math import ceil
from engineio.async_drivers import gevent  # this is needed for the error we got after freezing
from server import socket_io, oncher_app  # can be deleted
from os import _exit
import sentry_sdk

# import logging

sentry_sdk.init(
    "https://268b1e32fc164567b5ab73431b2741b0@o849618.ingest.sentry.io/5816571",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# logging stuff
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
#
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(message)s')
# ch.setFormatter(formatter)
#
# logger.addHandler(ch)

BASE_URL = None


# todo: add sentry logs

def start_server(port: int):
    # from server import socket_io, oncher_app
    socket_io.run(app=oncher_app, host='127.0.0.1',
                  port=port)  # , debug=True) => ValueError: signal only works in main thread
    return


def is_port_available(port: int):
    sock = socket(AF_INET, SOCK_STREAM)
    result = False
    try:
        sock.bind(("127.0.0.1", port))
        result = True
    except Exception:
        pass
    sock.close()
    return result


def destroy_window(ww):
    sleep(10)
    ww.destroy()
    return


def show_loading_screen():
    s_w, s_h = p.size()  # screen width and height
    # min(p.size()) // 2.5 = for my screen 307px
    square_size = 300  # todo: should it be hard coded or percentage of a screen
    start(destroy_window, create_window('',
                                        html=open('templates/loading.html').read(),
                                        x=(s_w // 2) - ceil(square_size // 2),
                                        y=(s_h // 2) - ceil(square_size // 2),
                                        width=square_size,
                                        height=square_size,
                                        frameless=True,
                                        resizable=False,
                                        # => on_top like zoom : https://github.com/r0x0r/pywebview/issues/476
                                        on_top=True))


def start_process(port):
    t = Thread(target=start_server, args=(port,))
    t.start()


def on_closed():
    # close the app if a single window is closed
    _exit(0)


# def hide(ws: List[webview.Window], show: bool = False):
#     print(ws, show)
#     if show:
#         [wx.show() for wx in ws]
#     else:
#         [wx.hide() for wx in ws]


if __name__ == '__main__':
    # special code-blocks for win platform
    # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
    # if sys.platform.startswith('win'):
    #     # On Windows calling this function is necessary.
    #     multiprocessing.freeze_support()
    #
    available_port = 5000
    # todo: to keep port 5000 , we need to save the PID when we had 5000 port and detach if is occupied
    while True:
        if is_port_available(available_port):
            break
        else:
            available_port += 1

    BASE_URL = "http://localhost:{}".format(available_port)
    print(f"BASE URL {BASE_URL}")
    # cef settings
    # settings.update({
    #     # 'remote_debugging_port':8080,
    #     # "debug": True,
    #     'persist_session_cookies': True,
    #     'cache_path': r'cef_cache'
    # })

    start_process(available_port)
    # t.join()

    # this is URL loading time before the window creation
    show_loading_screen()

    w, h = p.size()
    # w, h = w_a, h_a - int(h_a * 0.10)

    # first window
    w1x, w1y = 5, 5
    w1w, w1h = int(w * 0.24), int(h * 0.85) + int(h * 0.15) - 11
    # second window
    w2x, w2y = w1w, w1y
    w2w, w2h = int(w * 0.76) + 10, int(h * 0.85)
    # third window
    w3x, w3y = w1w, w2h - 30  # window three start y-co-ordinate looks like wrong!
    w3w, w3h = w2w, int(h * 0.15)

    _should_on_top = True

    second_window = create_window('',
                                  url=f"{BASE_URL}/window_2",
                                  x=w2x,
                                  y=w2y,
                                  width=w2w,
                                  frameless=True,
                                  height=w2h,
                                  resizable=False,
                                  on_top=_should_on_top)
    third_window = create_window('',
                                 url=f'{BASE_URL}/window_3',
                                 x=w3x,
                                 y=w3y,
                                 width=w3w,
                                 height=w3h,
                                 resizable=False,
                                 frameless=True,
                                 on_top=_should_on_top)
    first_window = create_window('',
                                 url=f'{BASE_URL}/window_1',
                                 x=w1x,
                                 y=w1y,
                                 width=w1w,
                                 height=w1h,
                                 frameless=True,
                                 resizable=False,
                                 on_top=_should_on_top)

    # https://stackoverflow.com/questions/65279193/how-to-close-pywebview-window-from-javascript-using-pywebview-api
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

    # app window closing, minimizing, maximizing, codes (for now we are getting signals from window 2)
    windows = [second_window, first_window, third_window]
    for window in windows:
        window.closed += on_closed


    @socket_io.on('close_window')
    def window_close(data):
        """
        don't write close_window() as it is a method of pywebview itself
        """
        try:
            # [win.destroy() for win in windows]
            _exit(0)
        except Exception as e:
            # todo: log to sentry
            print("Failed to destroy window because of {}".format(e))


    @socket_io.on('minimize_window')
    def window_minimize(data):
        try:
            # todo: Q: should all windows to be minimized?
            # todo: can we fix this "after minimizing when click on icon in pan/app bar then restore 3 windows all together"
            [win.minimize() for win in windows]
        except Exception as e:
            # todo: log to sentry
            print("Failed to minimize window because of {}".format(e))


    @socket_io.on('maximize_window')
    def window_maximize(data):
        """
        # presentation mode
        maximize window has two vital state => 1. Presentation mode type or normal mode
        """
        try:
            # todo: implement this functionality
            # if data['pos']:
            #     windows[1].hide()
            #     windows[2].hide()
            #     windows[0].resize()
            # else:
            #     windows[1].show()
            #     windows[2].show()
            #     windows[0].resize()
            pass
        except Exception as e:
            # todo: log to sentry
            print("Failed to maximize window because of {}".format(e))


    # func=hide, args=(windows, False),
    start(debug=True, gui="edgehtml")
