import pickle

from server import oncher_app, socket_io
from flask import jsonify, render_template
from flask_socketio import emit
import os
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
    return render_template('window3.html', BASE_URL=BASE_URL, colors=colors)


# this receives signal from the window3 to emit to window2 to simulate that action
@socket_io.on('navigation_signal_emit')
def pdf_signal_receive(data):
    print("navigation signal receive", data)
    emit("navigation_signal_receive",  # opposite meaning in terms of JS receiving
         {"action": data["data"]},  # action => previous_page, next_page
         namespace='/', broadcast=True)


# animation triggers

@socket_io.on('animation_trigger')
def animation_trigger_receive(data):
    print("animation trigger", data)
    emit("animation_trigger_emit_to_win2",
         {"animation_type": data['data']},
         namespace='/', broadcast=True)


@socket_io.on('timer_trigger')
def timer_trigger(data):
    start_or_end = data['start_or_end']
    print(start_or_end)
    t = {"start_or_end": start_or_end}
    if start_or_end == "start":
        pickle_path = 'start_timer.pickle'
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as handle:
                t['timer_data'] = pickle.load(handle)
                print(t['timer_data'])
        else:
            t['timer_data'] = "None"
    emit('timer_trigger_emit_to_win2', t, namespace='/', broadcast=True)


@socket_io.on('open_time_settings')
def open_time_settings(data):
    # same as top route but send timer_data: None
    t = {"start_or_end": '', 'timer_data': "None"}
    emit('timer_trigger_emit_to_win2', t, namespace='/', broadcast=True)


# drawing tools triggers
@socket_io.on('drawing_tools_signal_receive')
def drawing_tools_signal_receive(data):
    print(data)
    payload = {
        "type_of_action": data['type_of_action']
    }
    if data['type_of_action'] == 'color_change':
        payload['color'] = data['color']  # if color_change action then we insert color in the payload
    elif data['type_of_action'] == 'thickness_size':
        payload['thickness_size'] = data['thickness_size']

    emit('drawing_tools_trigger', payload, namespace='/', broadcast=True)
