from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
# (SỬA) Import đúng tên Model
from app.models.class_model import ClassModel 
from app.forms import ClassForm
from app.decorators import admin_required

# (SỬA) Đặt tên blueprint rõ ràng hơn, ví dụ 'class_admin'
class_bp = Blueprint('class_admin', __name__, url_prefix='/admin/classes')

@class_bp.route('/')
@login_required
def list_classes():
    """Hiển thị danh sách các lớp."""
    # (SỬA) Dùng ClassModel
    classes = ClassModel.query.order_by(ClassModel.name).all()

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

    # Kiểm tra quyền: Admin có thể xem tất cả, Leader chỉ xem lớp được phân công, Guest chỉ xem
    if current_user.is_admin():
        # Admin xem tất cả
        pass
    elif current_user.role in ('huynh_truong', 'du_truong'):
        # Leader chỉ xem lớp được phân công
        assigned_class_ids = [c.id for c in current_user.assigned_classes.all()]
        classes = [c for c in classes if c.id in assigned_class_ids]
    elif current_user.role == 'guest':
        # Guest có thể xem tất cả lớp
        pass
    else:
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('main_routes.home'))

    # (SỬA) Sửa đường dẫn template cho nhất quán
    return render_template('admin/class_list.html', title='Quản lý Lớp học', classes=classes, attendance_summary=attendance_summary)

@class_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    """Thêm lớp học mới."""
    form = ClassForm()
    if form.validate_on_submit():
        # (SỬA) Dùng ClassModel
        new_class = ClassModel(name=form.name.data)
        db.session.add(new_class)
        db.session.commit()
        flash('Đã thêm lớp học mới thành công!', 'success')
        return redirect(url_for('class_admin.list_classes'))
    # (SỬA) Sửa đường dẫn template cho nhất quán
    return render_template('admin/class_form.html', title='Thêm Lớp học', form=form, legend='Thêm Lớp học mới')

@class_bp.route('/<int:class_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_class(class_id):
    """Cập nhật tên lớp học."""
    # (SỬA) Dùng ClassModel
    class_obj = ClassModel.query.get_or_404(class_id)
    form = ClassForm(obj=class_obj)
    
    if form.validate_on_submit():
        class_obj.name = form.name.data
        db.session.commit()
        flash('Tên lớp đã được cập nhật!', 'success')
        return redirect(url_for('class_admin.list_classes'))
    
    # (SỬA) Sửa đường dẫn template cho nhất quán
    return render_template('admin/class_form.html', title='Cập nhật Lớp học', form=form, legend=f'Cập nhật: {class_obj.name}')

@class_bp.route('/<int:class_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_class(class_id):
    """Xóa lớp học (chỉ khi không còn thiếu nhi VÀ không còn HT/DT)."""
    # (SỬA) Dùng ClassModel
    class_obj = ClassModel.query.get_or_404(class_id)
    
    # (SỬA) Kiểm tra cả student và leader (dùng .first() cho hiệu quả)
    if class_obj.students.first():
        flash('Không thể xóa. Vẫn còn thiếu nhi trong lớp học này.', 'danger')
    elif class_obj.leaders.first():
        flash('Không thể xóa. Vẫn còn Huynh/Dự Trưởng được phân công vào lớp này.', 'danger')
    else:
        # Nếu an toàn, tiến hành xóa
        db.session.delete(class_obj)
        db.session.commit()
        flash('Lớp học đã được xóa!', 'success')

    return redirect(url_for('class_admin.list_classes'))

def view_details(class_id):
    """Trang xem chi tiết một lớp, danh sách thiếu nhi, điểm số..."""
    # (SỬA) Dùng ClassModel
    class_obj = ClassModel.query.get_or_404(class_id)
    students = class_obj.students.all()
    # (SỬA) Sửa đường dẫn template cho nhất quán
    return render_template('class/class_detail.html', class_obj=class_obj, students=students)

def manage_all():
    """Trang quản lý tất cả các lớp học."""
    classes = ClassModel.query.order_by(ClassModel.name).all()
    return render_template('admin/class_list.html', title='Quản lý Lớp học', classes=classes)

def assign_leader():
    """Trang phân công Huynh trưởng/Dự trưởng vào lớp."""
    from app.controllers.admin_controller import assign_leader as admin_assign_leader
    return admin_assign_leader()
