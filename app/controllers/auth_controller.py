from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.models.user import User
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tài khoản của bạn đã được tạo! Bây giờ bạn có thể đăng nhập.', 'success')
        return redirect(url_for('auth.login'))
    # THAY ĐỔI DÒNG NÀY
    return render_template('auth/register.html', title='Đăng ký', form=form)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Đăng nhập thành công!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Đăng nhập không thành công. Vui lòng kiểm tra email và mật khẩu.', 'danger')
    # VÀ THAY ĐỔI DÒNG NÀY
    return render_template('auth/login.html', title='Đăng nhập', form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))