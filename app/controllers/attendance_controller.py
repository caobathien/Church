from flask import Blueprint, abort, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.class_model import ClassModel
from app.forms import AttendanceForm, BulkAttendanceForm
from app.decorators import admin_required, permission_required_for_class
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/class/<int:class_id>/attendance', methods=['GET', 'POST'])
@login_required
@permission_required_for_class()
def take_attendance(class_id):
    """
    Trang điểm danh cho một lớp.
    Chỉ Admin và Huynh trưởng của lớp đó mới được truy cập. Guest chỉ xem.
    """
    if current_user.role == 'guest':
        flash('Bạn không có quyền điểm danh.', 'danger')
        abort(403)
    class_obj = ClassModel.query.get_or_404(class_id)
    students = class_obj.students.all()

    form = AttendanceForm()
    if form.validate_on_submit():
        attendance_date = form.date.data

        # Kiểm tra xem đã điểm danh cho ngày này chưa
        existing_attendance = Attendance.query.filter_by(
            class_id=class_id,
            date=attendance_date
        ).first()

        if existing_attendance:
            flash('Đã điểm danh cho ngày này rồi!', 'warning')
            return redirect(url_for('attendance.take_attendance', class_id=class_id))

        # Tạo bản ghi điểm danh cho từng học sinh
        for student in students:
            status = request.form.get(f'status_{student.id}', 'present')
            attendance = Attendance(
                student_id=student.id,
                class_id=class_id,
                date=attendance_date,
                status=status,
                created_by=current_user.id
            )
            db.session.add(attendance)

        db.session.commit()
        flash('Điểm danh thành công!', 'success')
        return redirect(url_for('main_routes.view_class', class_id=class_id))

    return render_template('attendance/take_attendance.html',
                         title=f'Điểm danh lớp {class_obj.name}',
                         form=form,
                         class_obj=class_obj,
                         students=students)

@attendance_bp.route('/class/<int:class_id>/attendance/<date_str>', methods=['GET', 'POST'])
@login_required
@permission_required_for_class(allow_guest=True)
def edit_attendance(class_id, date_str):
    """
    Trang chỉnh sửa điểm danh cho một ngày cụ thể.
    """
    if current_user.role == 'guest' and request.method == 'POST':
        flash('Bạn không có quyền chỉnh sửa điểm danh.', 'danger')
        abort(403)
    class_obj = ClassModel.query.get_or_404(class_id)
    students = class_obj.students.all()

    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Ngày không hợp lệ!', 'danger')
        return redirect(url_for('main_routes.view_class', class_id=class_id))

    # Lấy điểm danh hiện tại
    attendances = {att.student_id: att for att in Attendance.query.filter_by(
        class_id=class_id,
        date=attendance_date
    ).all()}

    form = BulkAttendanceForm()
    if form.validate_on_submit():
        # Cập nhật điểm danh
        for student in students:
            status = request.form.get(f'status_{student.id}', 'present')
            if student.id in attendances:
                attendances[student.id].status = status
            else:
                attendance = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    date=attendance_date,
                    status=status,
                    created_by=current_user.id
                )
                db.session.add(attendance)

        db.session.commit()
        flash('Cập nhật điểm danh thành công!', 'success')
        return redirect(url_for('main_routes.view_class', class_id=class_id))

    return render_template('attendance/edit_attendance.html',
                         title=f'Chỉnh sửa điểm danh {attendance_date.strftime("%d-%m-%Y")}',
                         form=form,
                         class_obj=class_obj,
                         students=students,
                         attendances=attendances,
                         attendance_date=attendance_date)

@attendance_bp.route('/class/<int:class_id>/attendance/history')
@login_required
@permission_required_for_class(allow_guest=True)
def attendance_history(class_id):
    """
    Trang xem lịch sử điểm danh của lớp.
    """
    class_obj = ClassModel.query.get_or_404(class_id)

    # Lấy tất cả ngày có điểm danh
    dates = db.session.query(Attendance.date).filter_by(class_id=class_id).distinct().order_by(Attendance.date.desc()).all()
    dates = [d[0] for d in dates]

    # Lấy thống kê điểm danh
    attendance_stats = {}
    for date in dates:
        attendances = Attendance.query.filter_by(class_id=class_id, date=date).all()
        total = len(attendances)
        present = sum(1 for att in attendances if att.status == 'present')
        absent = sum(1 for att in attendances if att.status == 'absent')
        late = sum(1 for att in attendances if att.status == 'late')
        attendance_stats[date] = {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'present_rate': round(present / total * 100, 1) if total > 0 else 0
        }

    return render_template('attendance/history.html',
                         title=f'Lịch sử điểm danh lớp {class_obj.name}',
                         class_obj=class_obj,
                         dates=dates,
                         attendance_stats=attendance_stats)
