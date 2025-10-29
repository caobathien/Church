from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.announcement import Announcement
from app.models.feedback import Feedback
from app.models.leader import Leader
from app.models.user import User
from app.models.user_profile import UserProfile
from app.forms import FeedbackForm

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=['GET', 'POST'])
@login_required
def home():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(content=form.content.data, sender=current_user)
        db.session.add(feedback)
        db.session.commit()
        flash('Phản hồi của bạn đã được gửi. Cảm ơn bạn!', 'success')
        return redirect(url_for('main.home'))

    # Lấy tất cả thông báo, sắp xếp mới nhất lên đầu
    announcements = Announcement.query.order_by(Announcement.timestamp.desc()).all()

    # Lấy danh sách Huynh Trưởng & Dự Trưởng
    leaders = Leader.query.join(User).join(UserProfile).all()

    # Lấy thống kê điểm danh cho tất cả lớp
    from app.models.class_model import ClassModel
    from app.models.attendance import Attendance
    from sqlalchemy import func

    classes = ClassModel.query.all()
    attendance_summary = {}
    total_attendance_days = 0

    for class_obj in classes:
        # Đếm số ngày đã điểm danh cho lớp này
        attendance_days = db.session.query(func.count(func.distinct(Attendance.date))).filter_by(class_id=class_obj.id).scalar()
        attendance_summary[class_obj.id] = {
            'name': class_obj.name,
            'attendance_days': attendance_days,
            'students_count': class_obj.students.count()
        }
        total_attendance_days += attendance_days

    return render_template('home.html', title="Trang chủ", announcements=announcements, form=form, leaders=leaders, attendance_summary=attendance_summary, total_attendance_days=total_attendance_days)
