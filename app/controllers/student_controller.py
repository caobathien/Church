from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.decorators import admin_required
from app.models.student import Student
from app.forms import StudentForm
from flask_login import login_required

# Tạo một Blueprint tên là 'student'
student_bp = Blueprint('student', __name__)

@student_bp.route("/")
@student_bp.route("/students")
@login_required
def list_students():
    """Hiển thị danh sách tất cả sinh viên."""
    students = Student.query.all()
    return render_template('students.html', students=students, title="Danh sách sinh viên")

@student_bp.route("/student/add", methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    """Thêm một sinh viên mới."""
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            student_code=form.student_code.data,
            full_name=form.full_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            class_name=form.class_name.data,
            gpa=form.gpa.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Đã thêm sinh viên mới thành công!', 'success')
        return redirect(url_for('student.list_students'))
    return render_template('student_form.html', title='Thêm sinh viên', form=form, legend='Thêm sinh viên')

@student_bp.route("/student/<int:student_id>/update", methods=['GET', 'POST'])
@login_required
@admin_required
def update_student(student_id):
    """Cập nhật thông tin sinh viên."""
    student = Student.query.get_or_404(student_id)
    # Tải dữ liệu của sinh viên có sẵn vào form
    form = StudentForm(obj=student)
    
    if form.validate_on_submit():
        # Cập nhật dữ liệu từ form vào đối tượng student
        student.student_code = form.student_code.data
        student.full_name = form.full_name.data
        student.date_of_birth = form.date_of_birth.data
        student.gender = form.gender.data
        student.class_name = form.class_name.data
        student.gpa = form.gpa.data
        db.session.commit() # Lưu thay đổi vào database
        flash('Thông tin sinh viên đã được cập nhật!', 'success')
        return redirect(url_for('student.list_students'))

    # Nếu là lần đầu vào trang (GET request), hiển thị form với dữ liệu cũ
    return render_template('student_form.html', title='Cập nhật sinh viên', form=form, legend='Cập nhật sinh viên')

@student_bp.route("/student/<int:student_id>/delete", methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    """Xóa sinh viên."""
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Sinh viên đã được xóa!', 'success')
    return redirect(url_for('student.list_students'))