#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021

import os

import requests
from PIL import Image
from flask import jsonify
from flask import render_template
from flask import request
from flask_socketio import emit

from app import BASE_URL
from database_schema.models import *
from api.server_router_api.server import oncher_app, database_cluster, socket_io, logger


# from app import logger


@oncher_app.route('/window_1')
def window_1():
    # todo: there are 2 grade_lesson dict version. One is flashcard and another is docs(pdf, ppt)

    # docs (ppt, pdf) version
    grade_lessons_docs_version = {}  # dummy for now => {grade: [lessons in list]}
    study_material: StudyMaterials
    for study_material in StudyMaterials.query.all():
        if study_material.grade not in grade_lessons_docs_version:
            grade_lessons_docs_version[study_material.grade] = []
        grade_lessons_docs_version[study_material.grade].append(study_material.lesson)

    # flashcard version
    flashcard_folders = os.listdir(os.path.abspath(os.path.join('static', 'flashcards')))
    # folder name format is like => Grade_X_Lesson_Y => underscore (_) as a delimiter
    grade_lessons_flashcard_version = {}  # dummy for now => {grade: [lessons in list]}
    for folder_names in flashcard_folders:
        # print(folder_names)
        split = folder_names.split("_")  # [1] is grade name and [-1] is lesson
        if split[1] not in grade_lessons_flashcard_version.keys():
            grade_lessons_flashcard_version[split[1]] = []
        grade_lessons_flashcard_version[split[1]].append(split[-1])  # todo: should we append the src to load or plain

    students = [s.__dict__ for s in StudentsData.query.all()]
    [a.pop('_sa_instance_state') for a in students]
    # print(students)
    return render_template('window1.html', students=students,
                           BASE_URL=BASE_URL, grade_lessons_docs_version=grade_lessons_docs_version,
                           grade_lessons_flashcard_version=grade_lessons_flashcard_version)


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
    if form:
        database_cluster.session.add(StudentsData(name=form['student_name'],
                                                  age=int(form['student_age']),
                                                  gender=1 if form['gender'] == "male" else 0,
                                                  which_grade=int(form['student_grade']))
                                     )
        database_cluster.session.commit()
        return jsonify(status=1)
    return jsonify(status=0)


@oncher_app.route('/student_note_save', methods=['POST'])
def student_note_save():
    form = request.form
    q = StudentsData.query.filter_by(id=int(form['id'])).first()
    q.note_saved = form['note']
    database_cluster.session.commit()
    return ''


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
    student_object = student_object.__dict__
    student_object.pop('_sa_instance_state')
    payload = {
        "id": student_object['id'],
        "name": student_object['name'],
        "star": student_object['total_stars'],
        "diamond": student_object['total_stars'] // 10,
        # this is needed for window 3 screenshot purpose
        "full_student_object_in_dict_format": student_object
    }
    emit('select_student_signal_receive', payload, namespace='/', broadcast=True)


@socket_io.on('configure_signal_emitter')
def configure_signal_emitter(data):
    emit('configure_signal_receive', {}, namespace='/', broadcast=True)


@socket_io.on('view_ss_report_open_signal')
def view_ss_report_open_signal(data):
    student_data = data['current_student_object']
    student_report_objects = [s.__dict__ for s in StudentReports.query.filter_by(student_id=student_data['id']).all()]
    [a.pop('_sa_instance_state') for a in student_report_objects]
    emit('view_ss_report_open_signal_receive',
         {'student_report_objects': student_report_objects[::-1],  # in descending order of time
          'name': student_data['name']},
         namespace='/', broadcast=True)


# we need these vars
current_grade = None
current_lesson = None
current_type_of_grade_lesson = 'ppt_pdf'  # there will be 3 types: => students, flashcard & ppt/pdf # todo: use it


@socket_io.on('grade_lesson_select_signal_receive')
def grade_lesson_select_signal_receive(data):
    logger.debug("received ..... from select grade-lesson {}".format(data))
    # print("grade lesson select signal {}".format(data))
    """
    todo: there will be 3 types: => students, flashcard & ppt/pdf
    """
    # data => {'grade': X, 'lesson': Y}
    # print(data)
    # folder name format is like => Grade_X_Lesson_Y => underscore (_) as a delimiter
    assert data['grade'] and data['lesson'], "Invalid grade/lesson due to null value"

    # student version
    students = [s.__dict__ for s in StudentsData.query.filter_by(which_grade=int(data['grade'])).all()]
    [a.pop('_sa_instance_state') for a in students]
    # print("students after selecting grade and lesson is {}".format(students))
    emit('students_list_update', {'students': students}, namespace='/', broadcast=True)

    # flashcard version
    folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=data['grade'],
                                                         lesson=data['lesson'])  # what if one of them is null?
    full_path = os.path.abspath(os.path.join('static', 'flashcards', folder_name))
    if os.path.exists(full_path):
        files_path = os.listdir(full_path)
        # print("files path {}".format(files_path))
        # a = "https://images.fineartamerica.com/images/artworkimages/mediumlarge/2/lexa-tabby-cat-painting-dora-hathazi-mendes.jpg"
        payload = ['/static/flashcards/{}/{}'.format(folder_name, f) for f in files_path]
        # print("flashcard payload {}".format(payload))
        # this is for games
        emit('grade_and_lesson_change', payload, namespace='/', broadcast=True)
    else:
        # print("Path {} doesn't exist for Flashcard".format(full_path))
        pass

    # this is for ppt and pdf (docs)

    # # below 2 vars will gen urls like => "/static/cache/test.pdf/0.jpg, /static/cache/test.pdf/1.jpg"
    # payload['parsed_pdf_dir_path'] = "/static/cache/{}".format(pdf_file_name)
    # payload['page_count'] = page_count
    # payload['width'] = w
    # payload['height'] = h
    study_mat_query = StudyMaterials.query.filter_by(grade=int(data['grade'])).filter_by(
        lesson=int(data['lesson'])).first()
    if study_mat_query:
        study_mat_query: StudyMaterials

        if study_mat_query.is_pdf:
            parsed_pdf_dir_path = "/static/cache/{}".format(study_mat_query.folder_name)
            # we need to parse width and height from the doc
            path0 = os.path.abspath(os.path.join(*parsed_pdf_dir_path.split("/")))
            # print("Pdf path is {}".format(path0))
            width, height = Image.open(os.path.join(path0, os.listdir(path0)[0])).size
            # print("Parsed Width {} and Height {}".format(width, height))
            from app import BASE_URL
            # print("BASE {}".format(BASE_URL))
            if BASE_URL is None:
                BASE_URL = "http://localhost:5000"  # todo: fix this
            payload = {
                'is_pdf': True,  # todo: for now it is true but we need to work for the ppt and others related files
                'parsed_pdf_dir_path': parsed_pdf_dir_path,
                # these are specially for pdf file
                'base_url': BASE_URL,
                'page_count': study_mat_query.page_count,
                'width': width,
                'height': height
            }
        else:
            # this is ppt
            payload = {
                'is_pdf': False,  # todo: for now it is true but we need to work for the ppt and others related files
                'ppt_url': study_mat_query.ppt_server_url
            }
        emit('study_doc_update', payload, namespace='/', broadcast=True)
        emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/', broadcast=True)
    else:
        print("No docs available under this grade and lesson")

    # this is for the window 3 screen shot purpose, that we need lesson and window-2 error check for un-selected GL for flashcards
    emit('grade_lesson_update_trigger', {'lesson': data['lesson'],
                                         'grade': data['grade']},
         namespace='/',
         broadcast=True)

# @oncher_app.route('/test')
# def test():
#     from urllib.request import urlopen
#     link = "https://psg3-powerpoint.officeapps.live.com/p/PowerPointFrame.aspx?PowerPointView=SlideShowView&ui=en%2DGB&rs=en%2DGB&WOPISrc=http%3A%2F%2Fpsg3%2Dview%2Dwopi%2Ewopi%2Elive%2Enet%3A808%2Foh%2Fwopi%2Ffiles%2F%40%2FwFileId%3FwFileId%3Dhttps%253A%252F%252Fwww%252Elibwired%252Ecom%253A443%252Fstatic%252FGrade1Lesson1%252Epptx&access_token_ttl=0&wdModeSwitchTime=1612594467217"
#     response = urlopen(link)
#     html = response.read()
#     print(html)
#     return html
