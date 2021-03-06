from server import oncher_app, database_cluster
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
    return render_template('window1.html', students=StudentsData.query.all(),
                           BASE_URL=BASE_URL)


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
        src_to_load = r"""{}/static/js/ViewerJS/index.html#../../files/{}""".format(BASE_URL,file.filename)
        print(src_to_load)
    elif any([filename.endswith(extension) for extension in ['.ppt', '.pptx', '.pptm']]):
        # todo: here we need to upload the ppt.pptx to server then encode the server download url
        encoded_url = ""
        src_to_load = r"""https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"""

    emit("my response",
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
# @socket_io.on('message')
# def handle_message_2(data):
#     print('received message: ' + str(data))

@oncher_app.route('/test')
def test():
    from urllib.request import urlopen
    link = "https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"
    response = urlopen(link)
    html = response.read()
    print(html)
    return html
