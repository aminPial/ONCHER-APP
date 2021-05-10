from server import database_cluster


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
