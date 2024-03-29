from api.server_router_api.server import database_cluster
from datetime import datetime


# https://stackoverflow.com/questions/54820668/encrypting-data-into-postgres-and-decrypting-from-postgres-using-sqlalchemy-and
# todo: can we encrypt & decrypt columns..

class StudentsData(database_cluster.Model):
    id = database_cluster.Column(database_cluster.Integer, primary_key=True)

    name = database_cluster.Column(database_cluster.Text, nullable=False)
    age = database_cluster.Column(database_cluster.Integer, nullable=False)
    gender = database_cluster.Column(database_cluster.Integer, default=1)  # 1 means male 0 means female
    # recent lesson code
    recent = database_cluster.Column(database_cluster.Text, default="NULL")
    # how many classes already done/attended
    classes = database_cluster.Column(database_cluster.Integer, default=0)
    # how many classes are left
    left = database_cluster.Column(database_cluster.Integer, default=0)
    total_stars = database_cluster.Column(database_cluster.Integer, default=0)
    which_grade = database_cluster.Column(database_cluster.Integer, nullable=False)
    note_saved = database_cluster.Column(database_cluster.Text)


class StudyMaterials(database_cluster.Model):
    id = database_cluster.Column(database_cluster.Integer, primary_key=True)
    # todo: can there be ppt and pdf both under same grade and lesson?
    grade = database_cluster.Column(database_cluster.Integer)
    lesson = database_cluster.Column(database_cluster.Integer)
    folder_name = database_cluster.Column(database_cluster.Text)
    # is_flashcard = 0 or 1
    is_flashcard = database_cluster.Column(database_cluster.Integer, default=0)
    is_pdf = database_cluster.Column(database_cluster.Integer, default=1)
    # this is specific for PDF
    page_count = database_cluster.Column(database_cluster.Integer, default=0)
    # this is specific for ppt, .pptx and related files
    ppt_server_url = database_cluster.Column(database_cluster.Text)


class StudentReports(database_cluster.Model):
    id = database_cluster.Column(database_cluster.Integer, primary_key=True)
    when = database_cluster.Column(database_cluster.Text, default=datetime.now().strftime("%I:%M:%S %p %d %B,%Y"))
    student_id = database_cluster.Column(database_cluster.Integer, nullable=False)  # student id (primary key)
    report_saved = database_cluster.Column(database_cluster.Text)
