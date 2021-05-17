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
import fitz
from PIL import Image


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


# pdf file parser
def parse_pdf_file(pdf_file_path: str):
    """
    returns:
      pdf_file_path_after_parsing_to_images
      page counts of PDF
    """
    # create folder to save the images of the pdf file
    pdf_file_name = pdf_file_path.split('\\')[-1]
    print("pdf file name: {}".format(pdf_file_name))
    page_extract_directory = os.path.join(sys.path[0], 'static', 'cache', pdf_file_name)
    print("page extract directory: {}".format(page_extract_directory))
    if os.path.exists(page_extract_directory):
        # shutil.rmtree(page_extract_directory)
        images = os.listdir(page_extract_directory)
        w, h = Image.open(os.path.join(page_extract_directory, images[0])).size
        print("Image Size from Pre is {} {}".format(w, h))
        return pdf_file_name, len(images), w, h
    os.makedirs(page_extract_directory)

    doc = fitz.open(pdf_file_path)
    no_of_pages = doc.pageCount
    w, h = 0, 0
    for page_no, _ in enumerate(doc):
        print("Extracting {} Page no: {}".format(pdf_file_name, page_no))
        page = doc.loadPage(page_no)  # number of page
        """
            # https://stackoverflow.com/questions/46184239/extract-a-page-from-a-pdf-as-a-jpeg
            # https://stackoverflow.com/questions/63661910/convert-pdf-file-to-multipage-image
            # image = page.getPixmap(matrix=fitz.Matrix(150/72,150/72)) extracts the image at 150 DPI.
            # https://github.com/pymupdf/PyMuPDF/issues/181
        """
        # zoom = 2
        # mat = fitz.Matrix(zoom, zoom)
        pix = page.getPixmap(matrix=fitz.Matrix(6, 6))  # 300 DPI
        # change color channel accordingly, you can use png, jpg, jpeg
        output = os.path.join(page_extract_directory, "{}.png".format(page_no))
        pix.writePNG(output)
        im = Image.open(output)
        w, h = im.size
        print("Image Size: {} {}".format(w, h))

    return [pdf_file_name, no_of_pages, w, h]  # (pdf_file_name and pages count and image w & h)


@oncher_app.route('/upload_document', methods=['POST'])
def upload_document():
    # send "start showing loading animation" signal to window 2
    emit("ppt_or_ppt_upload_signal", {"is_loading": True},
         namespace='/',
         broadcast=True)

    file = request.files["myfile"]
    file: request.files
    filename = secure_filename(file.filename)
    full_file_path = os.path.join(sys.path[0], "static", "files", filename)
    file.save(full_file_path)

    # via "is_pdf": false or true we will know if it is pdf or ppt,pptx, pptm
    payload = {'is_pdf': False, "is_loading": False}

    if filename.endswith(".pdf"):
        # src_to_load = r"""{}/static/js/ViewerJS/index.html#../../files/{}""".format(BASE_URL, file.filename)
        # print(src_to_load)
        payload['is_pdf'] = True
        pdf_file_name, page_count, w, h = parse_pdf_file(full_file_path)
        # below 2 vars will gen urls like => "/static/cache/test.pdf/0.jpg, /static/cache/test.pdf/1.jpg"
        payload['parsed_pdf_dir_path'] = "/static/cache/{}".format(pdf_file_name)
        payload['page_count'] = page_count
        payload['width'] = w
        payload['height'] = h

    elif any([filename.endswith(extension) for extension in ['.ppt', '.pptx', '.pptm']]):
        # todo: here we need to upload the ppt.pptx to server then encode the server download url
        encoded_url = ""
        src_to_load = r"""https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"""
        payload["src_to_load"] = src_to_load

    emit("ppt_or_ppt_upload_signal",
         payload,
         namespace='/',
         broadcast=True)

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
