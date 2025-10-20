from app.models.student import Student
from app import db

class StudentService:
    @staticmethod
    def get_all_students():
        return Student.query.all()

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)

    @staticmethod
    def add_student(name, age, grade, email):
        student = Student(name=name, age=age, grade=grade, email=email)
        db.session.add(student)
        db.session.commit()

    @staticmethod
    def update_student(student, name, age, grade, email):
        student.name = name
        student.age = age
        student.grade = grade
        student.email = email
        db.session.commit()

    @staticmethod
    def delete_student(student):
        db.session.delete(student)
        db.session.commit()
