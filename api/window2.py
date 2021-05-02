# main screen
from flask_socketio import emit

from server import oncher_app, socket_io, database_cluster
from flask import render_template
import pickle
from flask import jsonify
from flask import request
from app import BASE_URL
from models import StudentsData


@oncher_app.route('/window_2')
def window_2():
    return render_template('window2.html', BASE_URL=BASE_URL)


@oncher_app.route('/save_time_count', methods=['POST'])
def save_time_count():
    f = request.form
    if f:
        a = {'hour': int(f['hour']), 'minutes': int(f['minutes']), 'seconds': int(f['seconds'])}
        # print(a)
        with open('start_timer.pickle', 'wb') as handle:
            pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return jsonify(status=1)
    else:
        return jsonify(status=0)


#
@socket_io.on('add_star_to_student_record')
def add_star_to_student_record(data):
    student_object = StudentsData.query.filter_by(id=data['id']).first()
    assert student_object is not None, "student object is null while adding star"
    student_object: StudentsData
    student_object.total_stars = student_object.total_stars + 1
    database_cluster.session.commit()
    return {}


@socket_io.on('game_4_initialize')
def game_4_initialize(data):
    print(data)
    emit('game_4_init_emit_signal', {'image_name': 'CAT' if 'image_name' not in data.keys() else data['image_name']},
         namespace='/', broadcast=True)
