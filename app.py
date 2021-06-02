import multiprocessing
import socket
import sys
import time
import pyautogui as p
import webview
from webview.platforms.cef import settings  #
from math import ceil

BASE_URL = None


# command_line_switches.update({
#     'disable-web-security': 'True'
# })
# web_security_disabled


def start_server(port: int):
    from server import socket_io, oncher_app
    socket_io.run(app=oncher_app, host='0.0.0.0', port=port)
    return


def is_port_available(port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except Exception:
        pass
    sock.close()
    return result


def destroy_window(window):
    time.sleep(5)
    window.destroy()
    return


def show_loading_screen():
    s_w, s_h = p.size()  # screen width and height
    square_size = 300
    webview.start(destroy_window, webview.create_window('',
                                                        html=open('templates/loading.html').read(),
                                                        x=(s_w // 2) - ceil(square_size // 2),
                                                        y=(s_h // 2) - ceil(square_size // 2),
                                                        width=square_size,
                                                        height=square_size,
                                                        frameless=True,
                                                        resizable=False))


if __name__ == '__main__':
    # special code-blocks for win platform
    # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()

    # show_loading_screen()

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
    settings.update({
        # 'remote_debugging_port':8080,
        # "debug": True,
        'persist_session_cookies': True,
        'cache_path': r'cef_cache'
    })

    t = multiprocessing.Process(target=start_server, args=(available_port,))
    t.start()
    # t.join()

    # this is URL loading time before the window creation
    time.sleep(6)  # todo: we will show a simple loading screen in this time

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
                                          url=f"{BASE_URL}/window_2",
                                          x=w2x,
                                          y=w2y,
                                          width=w2w,
                                          frameless=True,
                                          height=w2h,
                                          resizable=False)
    third_window = webview.create_window('',
                                         url=f'{BASE_URL}/window_3',
                                         x=w3x,
                                         y=w3y,
                                         width=w3w,
                                         height=w3h,
                                         resizable=False,
                                         frameless=True)
    first_window = webview.create_window('',
                                         url=f'{BASE_URL}/window_1',
                                         x=w1x,
                                         y=w1y,
                                         width=w1w,
                                         height=w1h,
                                         frameless=True,
                                         resizable=False)
    # https://stackoverflow.com/questions/65279193/how-to-close-pywebview-window-from-javascript-using-pywebview-api
    """
        Useful Links:
            1. https://www.programmersought.com/article/13205830225/ (nssm, service manager in windows)
        """
    webview.start(gui='cef', debug=True)
    t.close()
    t.terminate()
    sys.exit()
