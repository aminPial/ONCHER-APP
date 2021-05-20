from server import oncher_app, database_cluster, socket_io
from flask import render_template
from flask import request
from flask import jsonify
import os
import sys
from flask_socketio import emit
import requests
from models import StudentsData
from app import BASE_URL


@oncher_app.route('/window_1')
def window_1():
    # print(os.getcwd())
    grade_lesson_folders = os.listdir(os.path.join(sys.path[0], 'static', 'u_data'))
    # folder name format is like => Grade_X_Lesson_Y => underscore (_) as a delimiter
    grade_lessons = {}  # dummy for now => {grade: [lessons in list]}
    for folder_names in grade_lesson_folders:
        print(folder_names)
        split = folder_names.split("_")  # [1] is grade name and [-1] is lesson
        if split[1] not in grade_lessons.keys():
            grade_lessons[split[1]] = []
        grade_lessons[split[1]].append(split[-1])  # todo: should we append the src to load or plain
    students = [s.__dict__ for s in StudentsData.query.all()]
    [a.pop('_sa_instance_state') for a in students]
    print(students)
    return render_template('window1.html', students=students,
                           BASE_URL=BASE_URL, grade_lessons=grade_lessons)


def upload_ppt_to_server(local_file_location: str) -> bool:
    """

    :param local_file_location: this must be full path like os.path.join(sys.path[0], file_loc)
    :return:
    """
    if os.path.exists(local_file_location):
        url = 'http://httpbin.org/post'
        with open(local_file_location, 'rb') as file:
            files = {'file': file}
            r = requests.post(url, files=files)
            print(r.text)
            return True
    return False


@oncher_app.route('/add_student', methods=['POST'])
def add_student():
    form = request.form
    print(form)
    if form:
        database_cluster.session.add(StudentsData(name=form['student_name'],
                                                  age=int(form['student_age']),
                                                  gender=1 if form['gender'] == "male" else 0,
                                                  which_grade=int(form['student_grade']))
                                     )
        database_cluster.session.commit()
        return jsonify(status=1)
    return jsonify(status=0)


# @socket_io.on('my event')
# def handle_message(data):
#     print('received message: ' + str(data))
#
#

# student select signal receive
@socket_io.on('student_select_signal_receive')
def student_select_signal_receive(data):
    # print('received message: ' + str(data))
    # we need to emit it to window 2 (from window1)
    student_object = StudentsData.query.filter_by(id=data['id']).first()
    # print(student_object.__dict__)
    assert student_object is not None, "student object is None after selection"
    student_object: StudentsData
    payload = {
        "id": student_object.id,
        "name": student_object.name,
        "star": student_object.total_stars,
        "diamond": student_object.total_stars // 10
    }
    emit('select_student_signal_receive', payload, namespace='/', broadcast=True)


@socket_io.on('configure_signal_emitter')
def configure_signal_emitter(data):
    emit('configure_signal_receive', {}, namespace='/', broadcast=True)


# we need these vars
current_grade = None
current_lesson = None


@socket_io.on('grade_lesson_select_signal_receive')
def grade_lesson_select_signal_receive(data):
    # data => {'grade': X, 'lesson': Y}
    # print(data)
    # folder name format is like => Grade_X_Lesson_Y => underscore (_) as a delimiter
    assert data['grade'] and data['lesson'], "Invalid grade/lesson due to null value"
    folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=data['grade'],
                                                         lesson=data['lesson'])  # what if one of them is null?
    full_path = os.path.join(sys.path[0], 'static', 'u_data', folder_name)
    if os.path.exists(full_path):
        files_path = os.listdir(full_path)
        # print("files path {}".format(files_path))
        # a = "https://images.fineartamerica.com/images/artworkimages/mediumlarge/2/lexa-tabby-cat-painting-dora-hathazi-mendes.jpg"
        payload = ['/static/u_data/{}/{}'.format(folder_name, f) for f in files_path]
        print(len(payload))
        emit('grade_and_lesson_change', payload, namespace='/', broadcast=True)
    else:
        print("Path {} doesn't exist".format(full_path))
        return

# @oncher_app.route('/test')
# def test():
#     from urllib.request import urlopen
#     link = "https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"
#     response = urlopen(link)
#     html = response.read()
#     print(html)
#     return html
