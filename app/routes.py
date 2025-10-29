from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.controllers import student_controller, class_controller # Bạn sẽ cần tạo class_controller
from app.decorators import admin_required, permission_required_for_class, permission_required_for_student

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    """
    Trang chủ (Dashboard) sẽ hiển thị khác nhau tùy vai trò.
    """
    if current_user.is_admin():
        # Nếu là Admin, trả về dashboard của Admin
        return render_template('admin/dashboard.html')
    else:
        # Nếu là Huynh trưởng, hiển thị các lớp mình phụ trách
        my_classes = current_user.assigned_classes.all()
        return render_template('leader/dashboard.html', my_classes=my_classes)

@main.route('/class/<int:class_id>')
@login_required
@permission_required_for_class(allow_guest=True)  # <-- ÁP DỤNG LUẬT KIỂM TRA QUYỀN, cho phép guest xem
def view_class(class_id):
    """Trang xem chi tiết một lớp, danh sách thiếu nhi, điểm số..."""
    return class_controller.view_details(class_id)

@main.route('/class/<int:class_id>/add-student', methods=['GET', 'POST'])
@login_required
@permission_required_for_class()  # <-- KIỂM TRA QUYỀN TRÊN LỚP
def add_student_to_class(class_id):
    """Thêm một thiếu nhi mới vào lớp cụ thể này."""
    return student_controller.add_student(class_id=class_id) # Controller giờ cần nhận class_id

@main.route('/student/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required_for_student # <-- ÁP DỤNG LUẬT TRÊN THIẾU NHI
def edit_student(student_id):
    """Sửa thông tin của một thiếu nhi."""
    return student_controller.update_student(student_id)

@main.route('/student/<int:student_id>/delete', methods=['POST']) # Nên dùng POST để xóa
@login_required
@permission_required_for_student # <-- KIỂM TRA QUYỀN TRÊN THIẾU NHI
def delete_student(student_id):
    """Xóa một thiếu nhi khỏi lớp."""
    return student_controller.delete_student(student_id)

@main.route('/student/<int:student_id>/scores', methods=['GET', 'POST'])
@login_required
@permission_required_for_student # <-- KIỂM TRA QUYỀN TRÊN THIẾU NHI
def manage_student_scores(student_id):
    """Trang nhập/sửa điểm cho một thiếu nhi."""
    return student_controller.manage_scores(student_id) # Bạn sẽ tạo hàm này

@main.route('/students')
@login_required
def list_students():
    """Trang xem danh sách thiếu nhi (Guest có thể xem, nhưng không thêm/sửa/xóa)."""
    return student_controller.list_students()

@main.route('/admin/classes')
@login_required
@admin_required
def manage_classes():
    """Trang quản lý các lớp học: tạo, sửa, xóa lớp."""
    return class_controller.manage_all()

@main.route('/admin/assign-leader', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_leader():
    """Trang phân công Huynh trưởng/Dự trưởng vào lớp."""
    return class_controller.assign_leader()