import pyautogui as p
import webview
from server import socket_io, oncher_app
import multiprocessing
import sys

from webview.platforms.cef import settings, command_line_switches  #

settings.update({
    # 'remote_debugging_port':8080,
    # "debug": True,
    'persist_session_cookies': True,
    'cache_path': r'cef_cache'
})


# command_line_switches.update({
#     'disable-web-security': 'True'
# })


# web_security_disabled


def start_server():
    socket_io.run(app=oncher_app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    t = multiprocessing.Process(target=start_server)
    t.start()

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

    second_window = webview.create_window('',
                                          url="http://localhost:5000/window_2",
                                          x=w2x,
                                          y=w2y,
                                          width=w2w,
                                          frameless=True,
                                          height=w2h,
                                          resizable=False)
    third_window = webview.create_window('',
                                         url='http://localhost:5000/window_3',
                                         x=w3x,
                                         y=w3y,
                                         width=w3w,
                                         height=w3h,
                                         resizable=False,
                                         frameless=True)
    first_window = webview.create_window('',
                                         url='http://localhost:5000/window_1',
                                         x=w1x,
                                         y=w1y,
                                         width=w1w,
                                         height=w1h,
                                         frameless=True,
                                         resizable=False)
    # https://stackoverflow.com/questions/65279193/how-to-close-pywebview-window-from-javascript-using-pywebview-api
    webview.start(gui='cef')
    t.close()
    t.terminate()
    sys.exit()
