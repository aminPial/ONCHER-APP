from server import oncher_app, database_cluster, socket_io
from flask import render_template
from flask import request
from flask import jsonify
from werkzeug.utils import secure_filename
import os
import sys
from flask_socketio import emit
import requests
from models import StudentsData
from app import BASE_URL


@oncher_app.route('/window_1')
def window_1():
    grade_lessons = {5: [11, 12, 13], 6: [3, 4, 5]}  # dummy for now => {grade: [lessons in list]}
    return render_template('window1.html', students=StudentsData.query.all(),
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


@oncher_app.route('/upload_document', methods=['POST'])
def upload_document():
    file = request.files["myfile"]
    file: request.files
    filename = secure_filename(file.filename)
    file.save(os.path.join(sys.path[0], "static", "files", filename))
    print(filename)

    src_to_load = None
    if filename.endswith(".pdf"):
        src_to_load = r"""{}/static/js/ViewerJS/index.html#../../files/{}""".format(BASE_URL, file.filename)
        print(src_to_load)
    elif any([filename.endswith(extension) for extension in ['.ppt', '.pptx', '.pptm']]):
        # todo: here we need to upload the ppt.pptx to server then encode the server download url
        encoded_url = ""
        src_to_load = r"""https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"""

    emit("ppt_or_ppt_upload_signal",
         {"link": src_to_load},
         namespace='/', broadcast=True)

    return jsonify(status=1)


@oncher_app.route('/add_student', methods=['POST'])
def add_student():
    form = request.form
    print(form)
    if form:
        database_cluster.session.add(StudentsData(name=form['student_name'],
                                                  age=int(form['student_age']),
                                                  gender=1 if form['gender'] == "male" else 0))
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


# we need these vars
current_grade = None
current_lesson = None


@socket_io.on('grade_select_signal_receive')
def grade_select_signal_receive(data):
    print(data)
    a = 'https://i2.wp.com/files.123freevectors.com/wp-content/uploads/new/animals/370-cartoon-dog-vector-image.png?w=800&q=95'
    b = 'https://thumbs.dreamstime.com/b/cartoon-elephant-vector-illustration-cute-baby-friendly-smile-big-ears-66547601.jpg'
    payload = [
        [a if data['grade'] == 5 else b
         for _ in range(3)]
        for _ in range(3)]
    print(payload)
    emit('grade_and_lesson_change', payload, namespace='/', broadcast=True)


@socket_io.on('lesson_select_signal_receive')
def lesson_select_signal_receive(data):
    print(data)
    payload = []
    emit('grade_and_lesson_change', payload, namespace='/', broadcast=True)

# @oncher_app.route('/test')
# def test():
#     from urllib.request import urlopen
#     link = "https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"
#     response = urlopen(link)
#     html = response.read()
#     print(html)
#     return html
