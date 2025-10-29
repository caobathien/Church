from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models.leader import Leader
from app.models.user import User
from app.models.user_profile import UserProfile
from app.forms import AddLeaderForm
from app.decorators import admin_required

leader_bp = Blueprint('leader', __name__, url_prefix='/admin/leaders')

@leader_bp.route('/')
@login_required
@admin_required
def list_leaders():
    leaders = Leader.query.join(User).join(UserProfile).all()
    return render_template('admin/leader_list.html', title='Quản lý Huynh Trưởng & Dự Trưởng', leaders=leaders)

@leader_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_leader():
    form = AddLeaderForm()
    if form.validate_on_submit():
        # Create User
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data
        )
        # Create UserProfile
        new_profile = UserProfile(
            ho_ten=form.ho_ten.data,
            ten_thanh=form.ten_thanh.data,
            sdt=form.sdt.data,
            dia_chi=form.dia_chi.data
        )
        new_user.profile = new_profile
        
        # Create Leader
        new_leader = Leader(user=new_user, position=form.role.data)
        
        try:
            db.session.add(new_user)
            db.session.add(new_leader)
            db.session.commit()
            flash('Đã thêm Huynh Trưởng thành công!', 'success')
            return redirect(url_for('leader.list_leaders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {e}', 'danger')
    return render_template('admin/add_leader_form.html', title='Thêm Huynh Trưởng & Dự Trưởng', form=form)

@leader_bp.route('/<int:leader_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_leader(leader_id):
    leader = Leader.query.get_or_404(leader_id)
    user = leader.user
    form = AddLeaderForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.profile.ho_ten = form.ho_ten.data
        user.profile.ten_thanh = form.ten_thanh.data
        user.profile.sdt = form.sdt.data
        user.profile.dia_chi = form.dia_chi.data
        leader.position = form.role.data
        db.session.commit()
        flash('Đã cập nhật Huynh Trưởng!', 'success')
        return redirect(url_for('leader.list_leaders'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
        form.ho_ten.data = user.profile.ho_ten
        form.ten_thanh.data = user.profile.ten_thanh
        form.sdt.data = user.profile.sdt
        form.dia_chi.data = user.profile.dia_chi
    return render_template('admin/add_leader_form.html', title='Sửa Huynh Trưởng & Dự Trưởng', form=form)

@leader_bp.route('/<int:leader_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_leader(leader_id):
    leader = Leader.query.get_or_404(leader_id)
    user = leader.user
    try:
        db.session.delete(leader)
        db.session.delete(user)
        db.session.commit()
        flash('Đã xóa Huynh Trưởng!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('leader.list_leaders'))
