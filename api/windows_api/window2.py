#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

import multiprocessing
import os
import pickle
import shutil
import time
from typing import List

import fitz
import requests
from flask import jsonify
from flask import render_template
from flask import request
from flask_socketio import emit
from werkzeug.utils import secure_filename
from urllib.parse import quote
from json import loads

from app import BASE_URL
from api.database_schema.models import *
from api.server_router_api.server import oncher_app, database_cluster, socket_io, logger, \
    APP_DATA_FOLDER_PATH, RELEASE_BUILD


@oncher_app.route('/window_2')
def window_2():
    grade_lessons = {}  # dummy for now => {grade: Object itself]}
    ppt_pdf = 0
    flashcard = 0
    for study_material in StudyMaterials.query.all():
        if study_material.is_flashcard:
            flashcard += 1
        else:
            ppt_pdf += 1
        if study_material.grade not in grade_lessons.keys():
            grade_lessons['{}'.format(study_material.grade)] = []
        study_material = study_material.__dict__
        study_material.pop('_sa_instance_state')
        # type of grade key is <str> (not int)
        grade_lessons['{}'.format(study_material['grade'])].append(study_material)
    # print("grade lessons: {}".format(grade_lessons))
    return render_template('window2.html',
                           BASE_URL=BASE_URL,
                           grade_lessons=grade_lessons,
                           grade_lesson_load_count_ppt_pdf=ppt_pdf,
                           grade_lesson_load_count_flashcard=flashcard
                           )


# this is class timer
@oncher_app.route('/save_time_count', methods=['POST'])
def save_time_count():
    f = request.form
    if f:
        a = {'hour': int(f['hour']), 'minutes': int(f['minutes']), 'seconds': int(f['seconds'])}
        # print(a)
        with open(os.path.join(APP_DATA_FOLDER_PATH, 'static', 'pickles',
                               'start_timer.pickle') if RELEASE_BUILD else os.path.abspath(
            os.path.join('static', 'pickles', 'start_timer.pickle')), 'wb') as handle:
            pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return jsonify(status=1)
    else:
        return jsonify(status=0)


# this is screenshot saving interval timer
@oncher_app.route('/save_time_interval_of_screenshot', methods=['POST'])
def save_time_interval_of_screenshot():
    f = request.form
    if f:
        a = {'seconds': int(f['seconds'])}
        # print(a)
        with open(os.path.join(APP_DATA_FOLDER_PATH, 'static', 'pickles',
                               'screenshot_interval_time.pickle') if RELEASE_BUILD else
                  os.path.abspath(os.path.join('static', 'pickles', 'screenshot_interval_time.pickle')),
                  'wb') as handle:
            pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # we need to emit this to window 3
        emit('updated_ss_interval_time', a, namespace='/', broadcast=True)
        return jsonify(status=1)
    else:
        return jsonify(status=0)


@socket_io.on('timer_is_finished_trigger_9')
def timer_is_finished_trigger_9(_):
    # print("timer_is_finished trigger called")
    emit('timer_is_finished_normally', {}, namespace='/', broadcast=True)


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
    # print("Game 4 initializer {}".format(data))
    emit('game_4_init_emit_signal', {
        'image_name': 'NULL' if 'image_name' not in data.keys() else data['image_name']},
         namespace='/', broadcast=True)


def parse_pdf_block(data_block: dict, page_start: int, page_end: int, save_w_h: bool):
    """
    page_start
    page_end
    data_block = {'pdf_document_object': <OBJECT>, 'extract_directory':'....'}
    save_w_h
    """
    # b = open(data_block['pdf_file_path'], "rb").read()
    # pdf_document_object = fitz.open("pdf", b)
    pdf_document_object = fitz.open(data_block['pdf_file_path'])
    extract_directory = data_block['extract_directory']

    if pdf_document_object and extract_directory:
        logger.debug("Extracting PAGE {}-{} from PID: {}".format(page_start, page_end, os.getpid()))
        for page_no in range(page_start, page_end):
            # print("[+++++] PAGE NO: {}".format(page_no))
            page = pdf_document_object.loadPage(page_no)  # number of page
            """
                # https://stackoverflow.com/questions/46184239/extract-a-page-from-a-pdf-as-a-jpeg
                # https://stackoverflow.com/questions/63661910/convert-pdf-file-to-multipage-image
                # image = page.getPixmap(matrix=fitz.Matrix(150/72,150/72)) extracts the image at 150 DPI.
                # https://github.com/pymupdf/PyMuPDF/issues/181
            """
            # zoom = 2
            # mat = fitz.Matrix(zoom, zoom)
            # st = time.time()
            pix = page.getPixmap(matrix=fitz.Matrix(2, 2))  # 300 DPI
            # print("Zoom Time: {} sec".format(time.time() - st))
            # change color channel accordingly, you can use png, jpg, jpeg
            # st = time.time()
            pix.writePNG(os.path.join(extract_directory, "{}.png".format(page_no)))
            # threads.append(threading.Thread(target=write_png,
            #                                 args=(pix, ))

            # print("Write Time: {} sec".format(time.time() - st))
            # if save_w_h:
            #     # calculate w,h only for first page to reduce overhead
            #     im = Image.open(os.path.join(extract_directory, "{}.png".format(page_no))).size
            #     print("Image Size: {} {}".format(im[0], im[1]))


# pdf file parser
def parse_pdf_file(pdf_file_path: str, pdf_file_name: str):
    """
    returns:
      pdf_file_path_after_parsing_to_images
      page counts of PDF
    """
    # create folder to save the images of the pdf file
    # print("pdf file name: {}".format(pdf_file_name))
    extract_directory = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'cache', pdf_file_name) \
        if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'cache', pdf_file_name))
    # print("page extract directory: {}".format(extract_directory))
    # if os.path.exists(page_extract_directory):
    #     # shutil.rmtree(page_extract_directory)
    #     images = os.listdir(page_extract_directory)
    #     w, h = Image.open(os.path.join(page_extract_directory, images[0])).size
    #     print("Already Exists. Image Size from Pre is {} {}".format(w, h))
    #     return [pdf_file_name, len(images), w, h]
    if os.path.exists(extract_directory):
        shutil.rmtree(extract_directory)
    os.makedirs(extract_directory)

    # b = open(pdf_file_path, "rb").read()
    # pdf_document_object = fitz.open('pdf', b)
    pdf_document_object = fitz.open(pdf_file_path)
    no_of_pages = pdf_document_object.pageCount

    # print("NO OF PAGES: {}".format(no_of_pages))

    _divide_by_parts = 10
    pools = []
    # todo: use ProcessPool() for better efficiency
    # todo: write some and isolate this child process "parse_pdf and it's caller" routines
    pools: List[multiprocessing.Process]
    tail_size, partial = divmod(no_of_pages, _divide_by_parts)
    if tail_size == 0:
        _divide_by_parts = 1

    # print(tail_size, partial)
    st = time.time()
    # multiprocessing.freeze_support()
    for page_no in range(partial if tail_size == 0 else (tail_size + (1 if partial else 0))):
        start = page_no * _divide_by_parts
        end = ((page_no + 1) * _divide_by_parts)
        if end > no_of_pages:
            # print("End {} . No of Pages {}".format(end, no_of_pages))
            end = no_of_pages
        pools.append(multiprocessing.Process(target=parse_pdf_block,
                                             args=({'pdf_file_path': pdf_file_path,
                                                    'extract_directory': extract_directory, },
                                                   start,
                                                   end,
                                                   # save w, h if first page else don't
                                                   True if page_no == 0 else False)))
    [p.start() for p in pools]
    [p.join() for p in pools]
    logger.debug("Took {} seconds to parse the PDF".format(time.time() - st))
    return [pdf_file_name, no_of_pages]  # [file_name,page_count , W, H]


def upload_ppt(full_file_path, retry_count_left=5):
    if retry_count_left == 0:
        return {'status': 'failed'}
    print("Uploading {} to server...".format(full_file_path))
    files = {'doc': open(full_file_path, 'rb')}  # todo: memory leak
    values = {}  # {'key': value}
    # todo: we will need to change the server for long run
    url = "https://libwired.com/upload_ppt"
    try:
        response = requests.post(url, files=files, data=values)
        response = response.json()
        response['status'] = 'ok'
        return response
    except Exception as e:
        print("Error happened while uploading ppt {}".format(e))
        # print('Failed to Upload. Retrying {} time'.format(retry_count_left))
        # upload_ppt(full_file_path, retry_count_left - 1)
        return {'status': 'failed'}


@oncher_app.route('/upload_document', methods=['POST'])
def upload_document():
    # todo: update the grade and lesson list after the upload document
    # send "start showing loading animation" signal to window 2
    # emit("ppt_or_ppt_upload_signal", {"is_loading": True},
    #      namespace='/',
    #      broadcast=True)
    form = request.form
    should_emit_grade_lesson = True
    try:
        if form['is_flashcard'] == "true":
            folder_name = os.path.join(APP_DATA_FOLDER_PATH, 'static',
                                       "flashcards",
                                       "Grade_{}_Lesson_{}".format(
                                           form['grade'], form['lesson'])) if RELEASE_BUILD else os.path.abspath(
                os.path.join("static",
                             "flashcards",
                             "Grade_{}_Lesson_{}".format(
                                 form['grade'], form['lesson'])))
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            else:
                # todo: if exists, should we show some crappy alert that it exists
                logger.warning("Folder Already Exists")
                return jsonify(status=0, does_exist=True, reason="Grade and Lesson folder already exists")

            for i in range(3):
                for j in range(3):
                    file = request.files[f'flashcard_{i}_{j}_input']
                    file: request.files
                    filename = secure_filename(file.filename).lstrip().rstrip()
                    logger.debug("flashcard filename => {}".format(filename))

                    full_file_path = os.path.join(folder_name, "{}".format(filename))
                    file.save(full_file_path)

            # todo: check if same grade lesson exists
            database_cluster.session.add(StudyMaterials(grade=int(form['grade']),
                                                        lesson=int(form['lesson']),
                                                        is_flashcard=1,
                                                        is_pdf=0
                                                        ))
            database_cluster.session.commit()
            return jsonify(status=1, does_exist=False)
        else:
            # todo: check if same grade lesson exists
            file = request.files['myfile']
            file: request.files
            filename = secure_filename(file.filename).lstrip().rstrip().split(".")
            logger.debug("raw filename of pdf/ppt is {}".format(filename))
            filename = "".join(map(str, filename[:-1])) + "_{grade}_{lesson}.".format(grade=form['grade'],
                                                                                     lesson=form['lesson']) \
                       + filename[-1]
            logger.debug("new filename of pdf/ppt is {}".format(filename))

            full_file_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'files', filename) if RELEASE_BUILD else \
                os.path.abspath(os.path.join("static", "files", filename))
            file.save(full_file_path)

            if filename.endswith(".pdf"):
                # if already exists then we return
                if StudyMaterials.query.filter_by(folder_name=filename).first():
                    should_emit_grade_lesson = False
                    logger.warning("Same grade and lesson exist in database when adding ppt")
                    return jsonify(status=0, does_exist=True)

                pdf_file_name, page_count = parse_pdf_file(full_file_path, filename)
                database_cluster.session.add(StudyMaterials(grade=int(form['grade']),
                                                            lesson=int(form['lesson']),
                                                            folder_name=filename,
                                                            is_flashcard=0,
                                                            page_count=page_count,
                                                            is_pdf=1
                                                            ))
                database_cluster.session.commit()
                # todo: emit to update the docs in the dropdown to grade & lesson
                # print("After committing. {}".format(StudyMaterials.query.all()))
                return jsonify(status=1, does_exist=False, folder_name=filename)

            elif any([filename.endswith(extension) for extension in ['.ppt', '.pptx', '.pptm']]):
                st = time.time()
                response = upload_ppt(full_file_path)
                logger.info("response from server is {} in {} seconds".format(response, time.time() - st))
                if response and response['status'] == 'ok' and response['done_uploading']:
                    # https%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx
                    encoded_url = quote('https://libwired.com/static/{}'.format(filename), safe='')
                    logger.info("Encoded Url is {}".format(encoded_url))
                    # https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217
                    src_to_load = r"""https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3D{encoded_url}&access_token_ttl=0&wdModeSwitchTime=1612594467217""".format(
                        encoded_url=encoded_url
                    )
                    logger.info("Full Url {}".format(src_to_load))
                    database_cluster.session.add(StudyMaterials(grade=int(form['grade']),
                                                                lesson=int(form['lesson']),
                                                                folder_name=filename,
                                                                is_flashcard=0,
                                                                is_pdf=0,
                                                                ppt_server_url=src_to_load
                                                                ))
                    database_cluster.session.commit()
                    return jsonify(status=1, does_exist=False, folder_name=filename)

                else:
                    return jsonify(status=0, does_exist=False, folder_name='Failed to Upload.Try Again')
            else:
                return jsonify(status=0, does_exist=False, folder_name='invalid file extension')
    except Exception as e:
        should_emit_grade_lesson = False
        logger.exception("Failed to upload flashcard/ppt/pdf because of {}".format(e))
        return jsonify(status=0, does_exist=False, folder_name='Failed to Upload.Try Again')
    finally:
        # now the special grade lesson emitter
        if should_emit_grade_lesson:
            logger.debug("Emitting special grade-lesson bits from finally block")
            # {'type_of_document': pdf/ppt/flashcard, 'grade': number, 'lesson': number}
            emit('special_grade_or_lesson_add',
                 # flashcard vs 'ppt/pdf' is all it matters,
                 # ppt & pdf doesn't have separate meaning for this function
                 {'type_of_document': 'flashcard' if form['is_flashcard'] == "true" else 'ppt_pdf',
                  'grade': form['grade'],
                  'lesson': form['lesson']},
                 namespace='/',
                 broadcast=True)


@socket_io.on('refresh_grades_as_per_docs')
def refresh_grades_as_per_docs(data):
    emit('refresh_grade_on_docs', {}, namespace='/', broadcast=True)
    emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/',
         broadcast=True)  # back from games (back-to-lesson)


@oncher_app.route('/student_report_submit', methods=['POST'])
def student_report_submit():
    f = request.form
    f = loads(f['report'])  # json.loads()
    print(f, type(f))
    if f:
        for report in f:
            database_cluster.session.add(StudentReports(student_id=report['student-id'],
                                                        report_saved=report['report']))
        database_cluster.session.commit()
        return jsonify(status=1)
    return jsonify(status=0)


@socket_io.on('clear_grade_and_lesson_on_back_to_intro')
def clear_grade_and_lesson_on_back_to_intro(_):
    emit('refresh_grade_on_docs', {}, namespace='/', broadcast=True)


@socket_io.on('clear_window_3_game_4_text')
def clear_window_3_game_4_text(_):
    emit('clear_window_3_game_4_text_trigger', {}, namespace='/', broadcast=True)
