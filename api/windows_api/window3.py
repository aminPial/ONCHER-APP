#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

import os
import pickle
from datetime import datetime

import pyscreenshot as ImageGrab
from flask import render_template
from flask_socketio import emit

from api.server_router_api.server import oncher_app, socket_io, logger, \
    APP_DATA_FOLDER_PATH, RELEASE_BUILD
from app import BASE_URL


@oncher_app.route('/window_3')
def window_3():
    colors = [
        'red',
        'green',
        'blue',
        'black',
        'white',
        'purple',
        'cyan',
        'deeppink',
        'teal'
    ]
    seconds = 5
    pickle_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'pickles',
                               'screenshot_interval_time.pickle') if RELEASE_BUILD else \
        os.path.abspath(os.path.join('static', 'pickles', 'screenshot_interval_time.pickle'))
    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as handle:
            seconds = pickle.load(handle)['seconds']
    else:
        # else just create a fresh pickle
        with open(pickle_path, 'wb') as handle:
            pickle.dump({'seconds': seconds}, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # this is actually from window-2.py as an update emitter but we use here as default too
    # for avoiding many route
    emit('updated_ss_interval_time', {'seconds': seconds}, namespace='/', broadcast=True)
    return render_template('window3.html', BASE_URL=BASE_URL, colors=colors)


# this receives signal from the window3 to emit to window2 to simulate that action
@socket_io.on('navigation_signal_emit')
def pdf_signal_receive(data):
    emit("navigation_signal_receive",  # opposite meaning in terms of JS receiving
         {"action": data["data"]},  # action => previous_page, next_page
         namespace='/', broadcast=True)


# animation triggers

@socket_io.on('animation_trigger')
def animation_trigger_receive(data):
    emit("animation_trigger_emit_to_win2",
         {"animation_type": data['data']},
         namespace='/', broadcast=True)


@socket_io.on('screenshot_timer_settings')
def screenshot_timer_settings(data):
    payload = {'seconds': 5}
    pickle_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'pickles',
                               'screenshot_interval_time.pickle') if RELEASE_BUILD else \
        os.path.abspath(os.path.join('static', 'pickles', 'screenshot_interval_time.pickle'))

    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as handle:
            payload['seconds'] = pickle.load(handle)['seconds']
    else:
        # else just create a fresh pickle
        with open(pickle_path, 'wb') as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # print(f"payload before emitting screen-shot timer is {payload}")
    emit('open_screenshot_timer_settings', payload, namespace='/', broadcast=True)


@socket_io.on('timer_trigger')
def timer_trigger(data):
    start_or_end = data['start_or_end'].lstrip().rstrip()
    print("time triggered: {}".format(start_or_end))
    t = {"start_or_end": start_or_end}
    if start_or_end == "start":
        pickle_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'pickles',
                                   'start_timer.pickle') if RELEASE_BUILD else os.path.abspath(
            os.path.join('static', 'pickles', 'start_timer.pickle'))
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as handle:
                t['timer_data'] = pickle.load(handle)
                print("timer data after loading from pickle is ", t['timer_data'])
        else:
            t['timer_data'] = "None"
    print("t => {}".format(t))
    emit('timer_trigger_emit_to_win2', t, namespace='/', broadcast=True)


@socket_io.on('open_time_settings')
def open_time_settings(data):
    print(data)
    # same as top route but send timer_data: None
    t = {"start_or_end": '', 'timer_data': "None"}
    emit('timer_trigger_emit_to_win2', t, namespace='/', broadcast=True)


# drawing tools triggers
@socket_io.on('drawing_tools_signal_receive')
def drawing_tools_signal_receive(data):
    print("Drawing Tools Payload: {}".format(data))
    payload = {
        "type_of_action": data['type_of_action']
    }
    if data['type_of_action'] == 'color_change':
        payload['color'] = data['color']  # if color_change action then we insert color in the payload
    elif data['type_of_action'] == 'thickness_size':
        payload['thickness_size'] = data['thickness_size']

    emit('drawing_tools_trigger', payload, namespace='/', broadcast=True)


# K/A
@socket_io.on('k_a_switch')
def k_or_a_receive_signal(data):
    emit('k_a_emit_signal', {'k_or_a': data['k_or_a']}, namespace='/', broadcast=True)


# the below route is shifted to window1.py for easy management of
# grade-lesson change in games select
# @socket_io.on('switch_to_games_receive')
# def switch_to_games(data):
#     # todo: emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/', broadcast=True)
#     emit('switch_to_games_emit', {'': ''}, namespace='/', broadcast=True)


@socket_io.on('take_screenshot')
def take_screenshot(data):
    print("take-screenshot triggered...")
    form = data['full_student_object_in_dict_format']
    selected_lesson = data['selected_lesson']
    if data:
        # Student Name - Class number - Grade - Lesson - Date - Time
        # # part of the screen
        # im = ImageGrab.grab(bbox=(10, 10, 510, 510))  # X1,Y1,X2,Y2
        filename = f"{form['name']}-{form['classes']}-{form['which_grade']}-{selected_lesson}-{datetime.now().strftime('%d %B%Y %I.%M.%S')}.png"
        # TODO: WE NEED TO SEND TO A MORE OBVIOUS, SHALLOW FOLDER (NEED TO BE CHOSEN BY TEACHER)
        ImageGrab.grab().save(os.path.join(APP_DATA_FOLDER_PATH,
                                           'static',
                                           'screenshots',
                                           filename) if RELEASE_BUILD else os.path.abspath(
            os.path.join('static', 'screenshots', filename)))
        # emit to window 2 to show a dialog that screenshot has been taken
        # or show a notification from OS itself
        # from form.to_dict() we will get the necessary info in window 2
        # if only one time then we emit to window 2 for showing notifications
        if not data['is_continuous']:
            emit('screen_shots_taken', {'filename': filename}, namespace='/', broadcast=True)


@socket_io.on('pass_message_to_window_2')
def pass_message_to_window_2(data):
    if data['message'].startswith('No Students exist in Grade'):
        logger.warning("returning shitty no student exist message")
        return
    logger.debug("Passing Message {}".format(data))
    emit('receive_notification_message', data, namespace='/', broadcast=True)
