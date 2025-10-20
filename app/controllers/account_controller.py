from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models.user import User
from app.forms import UpdateAccountForm, ChangePasswordForm, AdminUpdateUserForm
from app.decorators import admin_required

account_bp = Blueprint('account', __name__)

# --- ROUTES CHO USER THÔNG THƯỜNG ---

@account_bp.route('/account', methods=['GET', 'POST'])
@login_required
def my_account():
    update_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    if update_form.validate_on_submit() and 'submit' in request.form:
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


# --- ROUTES CHO ADMIN ---

@account_bp.route('/admin/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', title='Quản lý Người dùng', users=users)

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