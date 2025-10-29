from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models.user import User
from app.forms import UpdateAccountForm, ChangePasswordForm, AdminUpdateUserForm
from app.decorators import admin_required
import os
import secrets
from PIL import Image

# Hàm hỗ trợ xử lý ảnh avatar
def save_picture(form_picture):
    """Hàm tối ưu và lưu ảnh avatar."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)

    # Resize ảnh về kích thước chuẩn (ví dụ: 200x200)
    output_size = (200, 200)
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
        print(f"Error deleting file {picture_path}: {e}")  # Ghi log lỗi

account_bp = Blueprint('account', __name__)

@account_bp.route('/account', methods=['GET', 'POST'])
@login_required
def my_account():
    update_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    if update_form.validate_on_submit() and 'submit' in request.form:
        # Xử lý avatar nếu có
        if update_form.avatar.data:
            # Xóa avatar cũ nếu có
            if current_user.profile.avatar_filename:
                delete_picture(current_user.profile.avatar_filename)
            # Lưu avatar mới
            picture_file = save_picture(update_form.avatar.data)
            if picture_file:
                current_user.profile.avatar_filename = picture_file

        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        flash('Thông tin tài khoản của bạn đã được cập nhật!', 'success')
        return redirect(url_for('account.my_account'))

    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if current_user.verify_password(password_form.current_password.data):
            current_user.password = password_form.new_password.data
            db.session.commit()
            flash('Mật khẩu của bạn đã được thay đổi!', 'success')
            return redirect(url_for('account.my_account'))
        else:
            flash('Mật khẩu hiện tại không đúng.', 'danger')

    elif request.method == 'GET':
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email

    return render_template('account.html', title='Tài khoản', update_form=update_form, password_form=password_form)


@account_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def user_list():
    from app.forms import SearchUserForm
    search_form = SearchUserForm(request.form if request.method == 'POST' else request.args)

    # Xử lý tìm kiếm và lọc
    search_term = None
    role_filter = None

    if request.method == 'POST' and 'submit_search' in request.form and search_form.validate():
        search_term = search_form.search_term.data
        role_filter = search_form.role_filter.data
    elif request.method == 'GET':
        search_term = request.args.get('search_term', None)
        role_filter = request.args.get('role_filter', None)
        if search_term:
            search_form.search_term.data = search_term
        if role_filter:
            search_form.role_filter.data = role_filter

    # Bắt đầu query
    query = User.query

    # Áp dụng bộ lọc tìm kiếm
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    # Áp dụng bộ lọc vai trò
    if role_filter:
        query = query.filter(User.role == role_filter)

    users = query.all()
    return render_template('admin/user_list.html', title='Quản lý Người dùng', users=users, search_form=search_form)

@account_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUpdateUserForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        db.session.commit()
        flash('Thông tin người dùng đã được cập nhật.', 'success')
        return redirect(url_for('account.user_list'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
    return render_template('admin/edit_user.html', title='Chỉnh sửa Người dùng', form=form, user=user)

@account_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Bạn không thể xóa chính mình.', 'danger')
        return redirect(url_for('account.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash('Người dùng đã được xóa.', 'success')
    return redirect(url_for('account.user_list'))