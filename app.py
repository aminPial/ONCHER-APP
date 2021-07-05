#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

# from multiprocessing import freeze_support, Process

BASE_URL = None

if __name__ == '__main__':
    # import sys
    # special code-blocks for win platform (needs to JUST after __name__ == "__main__")
    # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
    # needed for stop flashing console in windowed mode
    # see https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    #     https://stackoverflow.com/questions/24455337/pyinstaller-on-windows-with-noconsole-simply-wont-work
    # if sys.platform.startswith('win'):
    # On Windows calling this function is necessary.
    # freeze_support()

    import sentry_sdk

    sentry_sdk.init(
        "https://268b1e32fc164567b5ab73431b2741b0@o849618.ingest.sentry.io/5816571",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )

    import os

    # create db folder and static folder if first run
    db_folder_path = os.path.abspath('db_file')
    if not os.path.exists(db_folder_path):
        os.makedirs(db_folder_path)

    # clean the "previously debugged" static files
    static_sub_folders_to_clear = ['cache',  # pdfs parsed images
                                   'files',  # pdf,ppt itself
                                   'flashcards',  # flashcard images
                                   # 'pickles', # exclude pickles for now
                                   'screenshots'
                                   ]
    for sub_folder in static_sub_folders_to_clear:
        sub_folder_path = os.path.abspath(os.path.join('static', sub_folder))
        if not os.path.exists(sub_folder_path):
            os.makedirs(sub_folder_path)

    # don't remove this => from engineio.async_drivers import gevent
    # for 'invalid async mode error'
    # see https://stackoverflow.com/questions/54150895/valueerror-invalid-async-mode-specified-when-bundling-a-flask-app-using-cx-fr
    from engineio.async_drivers import gevent
    from socket import socket, AF_INET, SOCK_STREAM


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


    available_port = 5000
    # todo: to keep port 5000 , we need to save the PID when we had 5000 port
    #  and detach if is occupied
    while True:
        if is_port_available(available_port):
            break
        else:
            available_port += 1

    BASE_URL = "http://localhost:{}".format(available_port)

    # private var & methods here (after __name__ == '__main__')
    from api.server_router_api.server import socket_io, oncher_app, logger  # can be deleted

    logger.debug(f"BASE URL {BASE_URL}")

    from threading import Thread

    from time import sleep

    import pyautogui as p
    # see https://stackoverflow.com/questions/63681770/getting-error-when-using-pynput-with-pyinstaller
    from pynput import keyboard
    from webview import create_window, start
    # from webview.platforms.cef import settings  #
    from math import ceil

    from flask_socketio import emit


    def start_server(port: int):
        # from server import socket_io, oncher_app
        socket_io.run(app=oncher_app, host='127.0.0.1',
                      port=port)  # , debug=True) => ValueError: signal only works in main thread
        return


    def destroy_window(ww):
        sleep(7)
        ww.destroy()
        return


    def show_loading_screen():
        s_w, s_h = p.size()  # screen width and height
        # min(p.size()) // 2.5 = for my screen 307px
        square_size = int(min(p.size()) / 2.5)

        start(destroy_window, create_window('',
                                            html=open(
                                                os.path.abspath(os.path.join('templates', 'loading.html'))).read(),
                                            x=(s_w // 2) - ceil(square_size // 2),
                                            y=(s_h // 2) - ceil(square_size // 2),
                                            width=square_size,
                                            height=square_size,
                                            frameless=True,
                                            resizable=False,
                                            # => on_top like zoom : https://github.com/r0x0r/pywebview/issues/476
                                            on_top=True))


    def on_press(key):
        try:
            pass
        except AttributeError:
            if (key == keyboard.Key.right or key == keyboard.Key.left) and \
                    IS_WINDOW_2_ACTIVE and IS_PPT_ACTIVE:
                with oncher_app.app_context():
                    emit('left-right-key-press', {'key': 'L' if key == keyboard.Key.left else 'R'},
                         namespace='/',
                         broadcast=True)


    def listen_for_keyboard():
        listener = keyboard.Listener(
            on_press=on_press)
        listener.start()


    def start_process(port):
        t = Thread(target=start_server, args=(port,))
        t.start()


    def on_closed():
        # close the app if a single window is closed
        os._exit(0)


    # def hide(ws: List[webview.Window], show: bool = False):
    #     print(ws, show)
    #     if show:
    #         [wx.show() for wx in ws]
    #     else:
    #         [wx.hide() for wx in ws]

    def hide_stuffs():
        # todo: implement this
        pass


    IS_WINDOW_2_ACTIVE = False
    IS_PPT_ACTIVE = False

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
    listen_for_keyboard()
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

    # see https://stackoverflow.com/questions/65279193/how-to-close-pywebview-window-from-javascript-using-pywebview-api

    # app window closing, minimizing, maximizing, codes (for now we are getting signals from window 2)
    windows = [second_window, first_window, third_window]
    for window in windows:
        window.closed += on_closed


    @socket_io.on('close_window')
    def window_close(_):
        """
        don't write close_window() as it is a method of pywebview itself
        """
        try:
            # [win.destroy() for win in windows]
            os._exit(0)
        except Exception as e:
            logger.error("Failed to destroy window because of {}".format(e))


    @socket_io.on('minimize_window')
    def window_minimize(_):
        try:
            # todo: Q: should all windows to be minimized?
            # todo: can we fix this "after minimizing when click on icon in pan/app bar then restore 3 windows all together"
            [win.minimize() for win in windows]
            global IS_WINDOW_2_ACTIVE
            # IS_WINDOW_2_ACTIVE = False  # todo: how can we know that it was again maximized ?
        except Exception as e:
            logger.error("Failed to minimize window because of {}".format(e))


    @socket_io.on('maximize_window')
    def window_maximize(_):
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
            logger.error("Failed to maximize window because of {}".format(e))


    @socket_io.on('is_ppt_active')
    def is_ppt_active(_):
        global IS_PPT_ACTIVE
        IS_PPT_ACTIVE = True  # not data
        logger.info("IS PPT ACTIVE ", IS_PPT_ACTIVE)


    IS_WINDOW_2_ACTIVE = True
    # func=hide, args=(w v  windows, False)

    # see https://pywebview.flowrl.com/guide/renderer.html
    start(debug=True, gui="mshtml")  # windows 10 build: edgehtml windows 7,8 and MacOS: edgehtml
