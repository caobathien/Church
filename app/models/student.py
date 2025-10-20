from app import db

class Student(db.Model):
    """
    Lớp Student đại diện cho bảng sinh viên trong database.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    gpa = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Student('{self.full_name}', '{self.student_code}')"