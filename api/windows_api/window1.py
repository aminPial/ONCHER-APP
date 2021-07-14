#  Copyright (C) Oncher App - All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Oncher App Engineering Team <engineering.team@oncher.com>, 2021
import os

from PIL import Image
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import request
from flask_socketio import emit

from api.database_schema.models import *
from api.server_router_api.server import oncher_app, socket_io, logger, \
    RELEASE_BUILD, APP_DATA_FOLDER_PATH, database_cluster
from app import BASE_URL


# from app import logger
@oncher_app.route('/cache/loading_screen')
def serve_loading_screen():
    return send_from_directory(directory=os.path.join(APP_DATA_FOLDER_PATH,
                                                      'cache') if RELEASE_BUILD else os.path.abspath(
        os.path.join('.', 'cache')),
                               path='loading_screen.gif', as_attachment=True)


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
    flashcard_folders = os.listdir(os.path.join(APP_DATA_FOLDER_PATH, 'static', 'flashcards')
                                   if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'flashcards'))
                                   )
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
                           BASE_URL=BASE_URL,
                           grade_lessons_docs_version=grade_lessons_docs_version,
                           grade_lessons_flashcard_version=grade_lessons_flashcard_version)


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


# student select signal receive
@socket_io.on('student_select_signal_receive')
def student_select_signal_receive(data):
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
def configure_signal_emitter(_):
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


current_type_of_grade_lesson = ''  # there will be 3 types: => students, flashcard & ppt/pdf
current_grade = None
current_lesson = None


def check_if_flashcard_exists():
    if current_grade and current_lesson:
        flashcard_folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=current_grade,
                                                                       lesson=current_lesson)
        full_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'flashcards') \
            if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'flashcards', flashcard_folder_name))
        return os.path.exists(full_path)
    logger.warning("no grade lesson is selected to check for flashcard existence")
    return True  # when nothing is selected then


# below 2 routes -> 'switch_to_games_receive' and 'refresh_grades_as_per_docs' are important
# to update if we should emit signal for doc or flashcard

@socket_io.on('switch_to_games_receive')
def switch_to_games(_):
    global current_type_of_grade_lesson
    # this way we know when to update grade-lesson only for flashcard
    current_type_of_grade_lesson = 'flashcard'  # !important: this line is important
    # todo: emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/', broadcast=True)
    does_exist = check_if_flashcard_exists()
    emit('switch_to_games_emit', {'does_this_grade_lesson_has_flashcards': does_exist,
                                  }, namespace='/',
         broadcast=True)
    if does_exist:
        logger.debug("flashcard does exist")
        folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=current_grade,
                                                             lesson=current_lesson)
        full_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'flashcards') \
            if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'flashcards', folder_name))
        flashcard_urls = ['/static/flashcards/{}/{}'.format(folder_name, f)
                          for f in os.listdir(full_path)]
        if len(flashcard_urls) < 9:
            logger.warning("Flashcards are less than 9 cards. Exists: {}".format(len(flashcard_urls)))
        # what type of bogus fucking name is this?
        emit('grade_and_lesson_change', flashcard_urls,
             namespace='/',
             broadcast=True)


@socket_io.on('refresh_grades_as_per_docs')
def refresh_grades_as_per_docs(_):
    global current_type_of_grade_lesson
    # this way we know when to update grade-lesson only for ppt & pdf
    current_type_of_grade_lesson = 'ppt_pdf'  # !important: this line is important

    emit('refresh_grade_on_docs', {'does_this_grade_lesson_has_flashcards': check_if_flashcard_exists()}, namespace='/',
         broadcast=True)
    emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/',
         broadcast=True)  # back from games (back-to-lesson)


@socket_io.on('grade_lesson_select_signal_receive')
def grade_lesson_select_signal_receive(data):
    global current_grade, current_lesson
    current_grade = data['grade']
    current_lesson = data['lesson']

    logger.debug("grade lesson selected: {}".format(data))
    """
      todo: Question: there will be 3 types: => students, flashcard & ppt/pdf or 2 types?
    """
    # data => {'grade': X, 'lesson': Y}
    assert data['grade'] and data['lesson'], "Invalid grade/lesson due to null value"

    # student version (update student list)
    students = [s.__dict__ for s in StudentsData.query.filter_by(which_grade=int(data['grade'])).all()]
    [a.pop('_sa_instance_state') for a in students]
    # logger.debug("students after selecting grade and lesson is {}".format(students))
    emit('students_list_update', {'students': students, 'grade': data['grade']}, namespace='/', broadcast=True)

    # docs version
    if current_type_of_grade_lesson == 'flashcard':
        logger.debug("emitting grade-lesson signal for flashcard only")

        # folder name format is like => Grade_X_Lesson_Y => underscore (_) as a delimiter
        # todo: what if one of them is null?
        folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=data['grade'],
                                                             lesson=data['lesson'])
        full_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'flashcards') \
            if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'flashcards', folder_name))
        if os.path.exists(full_path):
            flashcard_urls = ['/static/flashcards/{}/{}'.format(folder_name, f)
                              for f in os.listdir(full_path)]
            if len(flashcard_urls) < 9:
                logger.warning("Flashcards are less than 9 cards. Exists: {}".format(len(flashcard_urls)))

            emit('grade_and_lesson_change', flashcard_urls,
                 namespace='/',
                 broadcast=True)
        else:
            logger.error("Path {} doesn't exist for Flashcard".format(full_path))
            pass

    else:
        logger.debug("emitting grade-lesson signal for ppt,pdf only")
        # show loading screen in window 2
        emit('study_doc_update', {'is_loading': True}, namespace='/', broadcast=True)
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
                web_path = "/static/cache/{}".format(study_mat_query.folder_name)
                # we need to parse width and height from the doc
                # os.path.abspath(os.path.join(*web_path.split("/")) -> means to get the abspath
                actual_path = os.path.abspath(os.path.join(APP_DATA_FOLDER_PATH, 'static', 'cache',
                                                           study_mat_query.folder_name)) \
                    if RELEASE_BUILD else os.path.abspath(os.path.join(*web_path.split("/")))

                width, height = Image.open(os.path.join(actual_path, os.listdir(actual_path)[0])).size
                logger.debug("Parsed Width {} and Height {}".format(width, height))

                payload = {
                    'is_pdf': True,  # todo: for now it is true but we need to work for the ppt and others related files
                    'parsed_pdf_dir_path': web_path,
                    # these are specially for pdf file
                    'base_url': "http://localhost:5000",  # todo: what if 5000 is acquired <- important
                    'page_count': study_mat_query.page_count,
                    'width': width,
                    'height': height,
                    'is_loading': False
                }
            else:
                # this is ppt
                payload = {
                    'is_pdf': False,
                    # todo: for now it is true but we need to work for the ppt and others related files
                    'ppt_url': study_mat_query.ppt_server_url,
                    'is_loading': False
                }
            emit('study_doc_update', payload, namespace='/', broadcast=True)
            emit('enable_doc_related_icon', {'should_enable': True, 'skip': []}, namespace='/', broadcast=True)
        else:
            logger.error("No docs available under this grade and lesson")

    # this is in general
    # this is for the window 3 screen shot purpose, that we need lesson and
    # window-2 error check for un-selected GL for flashcards
    flashcard_folder_name = 'Grade_{grade}_Lesson_{lesson}'.format(grade=data['grade'],
                                                                   lesson=data['lesson'])
    full_path = os.path.join(APP_DATA_FOLDER_PATH, 'static', 'flashcards') \
        if RELEASE_BUILD else os.path.abspath(os.path.join('static', 'flashcards', flashcard_folder_name))

    emit('grade_lesson_update_trigger', {'lesson': data['lesson'],
                                         'grade': data['grade'],
                                         # this 'does_this_grade_lesson_has_flashcards' var is important
                                         # because when a class is going on and teacher clicks on the games
                                         # we need to check if the current grade lesson has flashcard shit or not
                                         'does_this_grade_lesson_has_flashcards': os.path.exists(full_path)},
         namespace='/',
         broadcast=True)
