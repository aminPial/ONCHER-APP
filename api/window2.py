# main screen
import time

from flask_socketio import emit

from server import oncher_app, socket_io, database_cluster
from flask import render_template
import pickle
from werkzeug.utils import secure_filename
from flask import jsonify
from flask import request
from app import BASE_URL
from models import StudentsData, StudyMaterials
import os
import sys
import fitz
from PIL import Image
import threading
import multiprocessing

import time


@oncher_app.route('/window_2')
def window_2():
    grade_lessons = {}  # dummy for now => {grade: Object itself]}
    # study_material: StudyMaterials
    for study_material in StudyMaterials.query.all():
        if study_material.grade not in grade_lessons.keys():
            grade_lessons['{}'.format(study_material.grade)] = []
        study_material = study_material.__dict__
        study_material.pop('_sa_instance_state')
        grade_lessons['{}'.format(study_material.grade)].append('{}'.format(
            study_material
        ))
    return render_template('window2.html', BASE_URL=BASE_URL, grade_lessons=grade_lessons)


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


PDF_GLOBAL = None
EXTRACT_DIRECTORY = ''
W = 0
H = 0


def parse_each_page(page_no: int):
    global PDF_GLOBAL
    global EXTRACT_DIRECTORY
    global W
    global H

    if PDF_GLOBAL and EXTRACT_DIRECTORY:
        print("Extracting Page no: {}".format(page_no))
        page = PDF_GLOBAL.loadPage(page_no)  # number of page
        """
            # https://stackoverflow.com/questions/46184239/extract-a-page-from-a-pdf-as-a-jpeg
            # https://stackoverflow.com/questions/63661910/convert-pdf-file-to-multipage-image
            # image = page.getPixmap(matrix=fitz.Matrix(150/72,150/72)) extracts the image at 150 DPI.
            # https://github.com/pymupdf/PyMuPDF/issues/181
        """
        # zoom = 2
        # mat = fitz.Matrix(zoom, zoom)
        # st = time.time()
        pix = page.getPixmap(matrix=fitz.Matrix(6, 6))  # 300 DPI
        # print("Zoom Time: {} sec".format(time.time() - st))
        # change color channel accordingly, you can use png, jpg, jpeg
        # st = time.time()
        output = os.path.join(EXTRACT_DIRECTORY, "{}.png".format(page_no))
        pix.writePNG(output)
        # print("Write Time: {} sec".format(time.time() - st))
        if page_no == 0:
            # calculate w,h only for first page to reduce overhead
            im = Image.open(output)
            W, H = im.size
            print("Image Size: {} {}".format(W, H))


# pdf file parser
def parse_pdf_file(pdf_file_path: str, pdf_file_name: str):
    """
    todo: can we make it a background process?
    returns:
      pdf_file_path_after_parsing_to_images
      page counts of PDF
    """
    # create folder to save the images of the pdf file
    print("pdf file name: {}".format(pdf_file_name))
    page_extract_directory = os.path.join(sys.path[0], 'static', 'cache', pdf_file_name)
    print("page extract directory: {}".format(page_extract_directory))
    # if os.path.exists(page_extract_directory):
    #     # shutil.rmtree(page_extract_directory)
    #     images = os.listdir(page_extract_directory)
    #     w, h = Image.open(os.path.join(page_extract_directory, images[0])).size
    #     print("Already Exists. Image Size from Pre is {} {}".format(w, h))
    #     return [pdf_file_name, len(images), w, h]
    os.makedirs(page_extract_directory)
    global EXTRACT_DIRECTORY
    EXTRACT_DIRECTORY = page_extract_directory
    global PDF_GLOBAL
    PDF_GLOBAL = fitz.open(pdf_file_path)
    no_of_pages = PDF_GLOBAL.pageCount
    print("NO OF PAGES: {}".format(no_of_pages))
    for page_no in range(no_of_pages):
        # t1 = threading.Thread(target=parse_each_page, args=(page_no,))
        # t1.start()
        parse_each_page(page_no)
    print("W and H from Global is {} {}".format(W, H))
    return [pdf_file_name, no_of_pages, W, H]


@oncher_app.route('/upload_document', methods=['POST'])
def upload_document():
    # send "start showing loading animation" signal to window 2
    # emit("ppt_or_ppt_upload_signal", {"is_loading": True},
    #      namespace='/',
    #      broadcast=True)

    file = request.files["myfile"]
    file: request.files
    filename = secure_filename(file.filename)
    full_file_path = os.path.join(sys.path[0], "static", "files", filename)
    file.save(full_file_path)

    form = request.form
    print(request.form.to_dict())

    if filename.endswith(".pdf"):
        if StudyMaterials.query.filter_by(folder_name=filename).first():
            return jsonify(status=0, does_exist=True)

        # src_to_load = r"""{}/static/js/ViewerJS/index.html#../../files/{}""".format(BASE_URL, file.filename)
        # print(src_to_load)
        start = time.time()
        pdf_file_name, page_count, w, h = parse_pdf_file(full_file_path, filename)
        print("[+++] Pdf parsing time {} sec.".format(time.time() - start))
        # # processing finished, parse_pdf_file() is done
        # # below 2 vars will gen urls like => "/static/cache/test.pdf/0.jpg, /static/cache/test.pdf/1.jpg"
        # payload['parsed_pdf_dir_path'] = "/static/cache/{}".format(pdf_file_name)
        # payload['page_count'] = page_count
        # payload['width'] = w
        # payload['height'] = h

        database_cluster.session.add(StudyMaterials(grade=int(form['grade_field']),
                                                    lesson=int(form['lesson_field']),
                                                    folder_name=filename,
                                                    is_flashcard=int(form['is_flashcard']),
                                                    page_count=page_count,
                                                    page_width=w,
                                                    page_height=h
                                                    ))
        database_cluster.session.commit()
        return jsonify(status=1, does_exist=False)

    # elif any([filename.endswith(extension) for extension in ['.ppt', '.pptx', '.pptm']]):
    #     # todo: here we need to upload the ppt.pptx to server then encode the server download url
    #     encoded_url = ""
    #     src_to_load = r"""https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"""
    #     payload["src_to_load"] = src_to_load

    # emit("ppt_or_ppt_upload_signal",
    #      payload,
    #      namespace='/',
    #      broadcast=True)


