from flask import Blueprint, render_template
from flask_login import login_required
from app.controllers import student_controller

main = Blueprint('main', __name__)

@main.route('/')
@login_required 
def index():
    return render_template('index.html')

@main.route('/students')
def students():
    return student_controller.list_students()

@main.route('/students/add', methods=['GET', 'POST'])
def add_student():
    return student_controller.add_student()

@main.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    return student_controller.edit_student(student_id)

@main.route('/students/delete/<int:student_id>')
def delete_student(student_id):
    return student_controller.delete_student(student_id)
