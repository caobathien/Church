from functools import wraps
from flask_login import current_user
from flask import abort, flash
from .models.student import Student
from .models.class_model import ClassModel

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Chức năng này yêu cầu quyền Admin.', 'danger')
            abort(403) # Lỗi Cấm truy cập
        return f(*args, **kwargs)
    return decorated_function

def permission_required_for_class(f):
    @wraps(f)
    def decorated_function(class_id, *args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        # Admin có toàn quyền
        if current_user.is_admin():
            return f(class_id, *args, **kwargs)

        # Guest có thể xem lớp nhưng không chỉnh sửa
        if current_user.role == 'guest':
            return f(class_id, *args, **kwargs)

        # Chỉ Huynh trưởng và Dự trưởng mới được phép điểm danh
        if not current_user.is_leader():
            flash('Chỉ Huynh trưởng và Dự trưởng mới được phép điểm danh.', 'danger')
            abort(403)

        # Kiểm tra xem user có phải là HT/DT và có được gán cho lớp này không
        is_assigned = current_user.assigned_classes.filter_by(id=class_id).first()

        if is_assigned:
            # Nếu được gán, cho phép truy cập
            return f(class_id, *args, **kwargs)

        # Nếu không, cấm
        flash('Bạn không có quyền điểm danh lớp này.', 'danger')
        abort(403)
    return decorated_function

def permission_required_for_student(f):
    @wraps(f)
    def decorated_function(student_id, *args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)

        # Admin có toàn quyền
        if current_user.is_admin():
            return f(student_id, *args, **kwargs)

        # Guest có thể xem học sinh nhưng không chỉnh sửa
        if current_user.role == 'guest':
            return f(student_id, *args, **kwargs)

        # Tìm lớp của Thiếu Nhi
        student = Student.query.get_or_404(student_id)
        if not student.class_id:
            flash('Học sinh này chưa được xếp lớp.', 'danger')
            abort(404) # Không tìm thấy

        # Kiểm tra xem user có phải là HT và có được gán cho lớp của SV này không
        class_id = student.class_id
        is_assigned = current_user.assigned_classes.filter_by(id=class_id).first()

        if is_assigned:
            # Nếu được gán, cho phép truy cập
            return f(student_id, *args, **kwargs)

        # Nếu không, cấm
        flash('Bạn không có quyền quản lý học sinh thuộc lớp này.', 'danger')
        abort(403)
    return decorated_function
