import os
import secrets
from flask import Blueprint, current_app, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models.announcement import Announcement
from app.models.feedback import Feedback
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.student import Student
from app.models.class_model import ClassModel
from app.forms import AnnouncementForm, AdminUpdateUserForm
from PIL import Image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- HÀM HỖ TRỢ XỬ LÝ ẢNH (Tối ưu) ---

def save_picture(form_picture):
    """Hàm tối ưu và lưu ảnh (Resize + Tạo tên ngẫu nhiên)."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

    # (Cải tiến) Resize ảnh về kích thước chuẩn (ví dụ: 1200px)
    output_size = (1200, 1200)
    try:
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    except Exception as e:
        flash(f'Lỗi xử lý ảnh: {e}', 'danger')
        return None
    
    return picture_fn

def delete_picture(filename):
    """Hàm hỗ trợ xóa file ảnh cũ một cách an toàn."""
    if not filename:
        return
    
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(picture_path):
            os.remove(picture_path)
    except Exception as e:
        print(f"Error deleting file {picture_path}: {e}") # Ghi log lỗi

# --- TRANG CHỦ ADMIN ---

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Trang chủ của Admin, hiển thị thông tin tổng quan."""
    user_count = User.query.count()
    student_count = Student.query.count()
    class_count = ClassModel.query.count()
    feedback_count = Feedback.query.count()
    
    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard',
                           user_count=user_count,
                           student_count=student_count,
                           class_count=class_count,
                           feedback_count=feedback_count)

# --- QUẢN LÝ HUYNH TRƯỞNG & DỰ TRƯỞNG (CRUD) ---

# Removed duplicate add_leader function, using the one in leader_controller.py instead

# --- QUẢN LÝ LỚP HỌC & PHÂN CÔNG ---

@admin_bp.route('/assign_leader', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_leader_to_class():
    """Trang phân công Huynh trưởng vào lớp."""
        
    # Lấy danh sách Huynh/Dự trưởng chưa được phân công vào lớp nào và các Lớp
    leaders = User.query.filter(User.role.in_(['huynh_truong', 'du_truong'])).filter(~User.assigned_classes.any()).all()
    classes = ClassModel.query.all()
    
    return render_template('admin/assign_leader.html',
                           title='Phân công Lớp',
                           leaders=leaders,
                           classes=classes)
                           # form=form)

# --- QUẢN LÝ LỚP HỌC ---

@admin_bp.route('/classes')
@login_required
@admin_required
def list_classes():
    """Trang danh sách các lớp học."""
    classes = ClassModel.query.all()

    # Lấy thống kê điểm danh cho từng lớp
    from app.models.attendance import Attendance
    from sqlalchemy import func
    attendance_summary = {}

    for class_obj in classes:
        # Đếm số ngày đã điểm danh cho lớp này
        attendance_days = db.session.query(func.count(func.distinct(Attendance.date))).filter_by(class_id=class_obj.id).scalar()
        attendance_summary[class_obj.id] = {
            'attendance_days': attendance_days
        }

    return render_template('admin/class_list.html', title='Quản lý Lớp học', classes=classes, attendance_summary=attendance_summary)

# --- QUẢN LÝ THÔNG BÁO (CRUD - Hoàn thiện) ---

@admin_bp.route('/announcement/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    """Tạo thông báo mới (Create)."""
    form = AnnouncementForm()
    if form.validate_on_submit():
        image_file = None
        if form.image.data:
            image_file = save_picture(form.image.data)
            
        announcement = Announcement(
            title=form.title.data, 
            content=form.content.data, 
            author=current_user,
            image_filename=image_file
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Thông báo đã được đăng!', 'success')
        return redirect(url_for('main.home'))
    return render_template('admin/announcement_form.html', title='Tạo thông báo', form=form, legend='Đăng thông báo mới')

@admin_bp.route('/announcement/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def update_announcement(announcement_id):
    """Sửa thông báo (Update)."""
    ann = Announcement.query.get_or_404(announcement_id)
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        if form.image.data:
            delete_picture(ann.image_filename) # Xóa ảnh cũ
            ann.image_filename = save_picture(form.image.data) # Lưu ảnh mới
            
        ann.title = form.title.data
        ann.content = form.content.data
        db.session.commit()
        flash('Đã cập nhật thông báo!', 'success')
        return redirect(url_for('main.home'))
        
    elif request.method == 'GET':
        form.title.data = ann.title
        form.content.data = ann.content
        
    return render_template('admin/announcement_form.html', title='Sửa thông báo', form=form, legend=f'Sửa: {ann.title}')

@admin_bp.route('/announcement/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """Xóa thông báo (Delete) - Đã sửa lỗi rò rỉ file."""
    ann = Announcement.query.get_or_404(announcement_id)
    
    # (Cải tiến) Xóa file ảnh liên quan
    delete_picture(ann.image_filename)
    
    db.session.delete(ann)
    db.session.commit()
    flash('Thông báo đã được xóa thành công.', 'success')
    return redirect(url_for('main.home'))

# --- QUẢN LÝ PHẢN HỒI ---

@admin_bp.route('/feedback')
@login_required
@admin_required
def view_feedback():
    """Xem danh sách phản hồi."""
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin/feedback_list.html', title='Danh sách Phản hồi', feedbacks=feedbacks)

@admin_bp.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_feedback(feedback_id):
    """Xóa phản hồi."""
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Phản hồi đã được xóa.', 'success')
    return redirect(url_for('admin.view_feedback'))

# --- QUẢN LÝ PHÂN CÔNG HUYNH TRƯỞNG VÀO LỚP ---

@admin_bp.route('/assign-leader', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_leader():
    """Trang phân công Huynh trưởng/Dự trưởng vào lớp."""
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        leader_id = request.form.get('leader_id')
        action = request.form.get('action')

        class_obj = ClassModel.query.get_or_404(class_id)
        user = User.query.get_or_404(leader_id)

        if action == 'assign':
            if user not in class_obj.leaders:
                class_obj.leaders.append(user)
                db.session.commit()
                flash(f'Đã phân công {user.profile.ho_ten} vào lớp {class_obj.name}.', 'success')
            else:
                flash(f'{user.profile.ho_ten} đã được phân công vào lớp {class_obj.name}.', 'warning')
        elif action == 'unassign':
            if user in class_obj.leaders:
                class_obj.leaders.remove(user)
                db.session.commit()
                flash(f'Đã gỡ phân công {user.profile.ho_ten} khỏi lớp {class_obj.name}.', 'success')
            else:
                flash(f'{user.profile.ho_ten} chưa được phân công vào lớp {class_obj.name}.', 'warning')

        return redirect(url_for('admin.assign_leader'))

    # GET request: Hiển thị danh sách lớp và Huynh trưởng chưa được phân công
    classes = ClassModel.query.all()
    leaders = User.query.filter(User.role.in_(['huynh_truong', 'du_truong'])).filter(~User.assigned_classes.any()).all()
    return render_template('admin/assign_leader.html', title='Phân công Huynh Trưởng', classes=classes, leaders=leaders)

@admin_bp.route('/class/<int:class_id>/leaders')
@login_required
@admin_required
def view_class_leaders(class_id):
    """Trang xem chi tiết Huynh trưởng/Dự trưởng được phân công vào một lớp."""
    class_obj = ClassModel.query.get_or_404(class_id)
    leaders = class_obj.leaders.all()
    return render_template('admin/class_leaders.html', title=f'Huynh Trưởng Lớp {class_obj.name}', class_obj=class_obj, leaders=leaders)
