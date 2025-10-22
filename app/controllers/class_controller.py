from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.models.class_model import Class
from app.forms import ClassForm
from app.decorators import admin_required

class_bp = Blueprint('class_admin', __name__, url_prefix='/admin/classes')

@class_bp.route('/')
@login_required
@admin_required
def list_classes():
    """Hiển thị danh sách các lớp."""
    classes = Class.query.order_by(Class.name).all()
    return render_template('class/class_list.html', title='Quản lý Lớp học', classes=classes)

@class_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    """Thêm lớp học mới."""
    form = ClassForm()
    if form.validate_on_submit():
        new_class = Class(name=form.name.data)
        db.session.add(new_class)
        db.session.commit()
        flash('Đã thêm lớp học mới thành công!', 'success')
        return redirect(url_for('class_admin.list_classes'))
    return render_template('class/class_form.html', title='Thêm Lớp học', form=form, legend='Thêm Lớp học')

@class_bp.route('/<int:class_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_class(class_id):
    """Cập nhật tên lớp học."""
    class_obj = Class.query.get_or_404(class_id)
    form = ClassForm(obj=class_obj)
    if form.validate_on_submit():
        class_obj.name = form.name.data
        db.session.commit()
        flash('Tên lớp đã được cập nhật!', 'success')
        return redirect(url_for('class_admin.list_classes'))
    return render_template('class/class_form.html', title='Cập nhật Lớp học', form=form, legend=f'Cập nhật Lớp: {class_obj.name}')

@class_bp.route('/<int:class_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_class(class_id):
    """Xóa lớp học (chỉ khi không còn sinh viên)."""
    class_obj = Class.query.get_or_404(class_id)
    if class_obj.students: # Kiểm tra xem lớp còn sinh viên không
        flash('Không thể xóa lớp học này vì vẫn còn sinh viên.', 'danger')
    else:
        db.session.delete(class_obj)
        db.session.commit()
        flash('Lớp học đã được xóa!', 'success')
    return redirect(url_for('class_admin.list_classes'))