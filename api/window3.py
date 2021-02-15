from server import oncher_app, socket_io
from flask import jsonify, render_template
from flask_socketio import emit


@oncher_app.route('/window_3')
def window_3():
    return render_template('window3.html')


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
