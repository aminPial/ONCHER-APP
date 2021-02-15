from server import database_cluster


class StudentsData(database_cluster.Model):
    id = database_cluster.Column(database_cluster.Integer, primary_key=True)

    name = database_cluster.Column(database_cluster.Text, nullable=False)
    age = database_cluster.Column(database_cluster.Integer, nullable=False)
    gender = database_cluster.Column(database_cluster.Integer, default=1)  # 1 means male 0 means female
    classes = database_cluster.Column(database_cluster.Integer, default=0)
    left = database_cluster.Column(database_cluster.Integer, default=0)
    total_stars = database_cluster.Column(database_cluster.Integer, default=0)
    total_diamond = database_cluster.Column(database_cluster.Integer, default=0)
