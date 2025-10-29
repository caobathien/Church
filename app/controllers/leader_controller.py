from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response, session
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.forms import AddLeaderForm
from app.decorators import admin_required
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
from werkzeug.utils import secure_filename

leader_bp = Blueprint('leader', __name__, url_prefix='/admin/leaders')

@leader_bp.route('/')
@login_required
@admin_required
def list_leaders():
    leaders = User.query.filter(User.role.in_(['huynh_truong', 'du_truong'])).join(UserProfile).all()
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
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Đã thêm Huynh Trưởng thành công!', 'success')
            return redirect(url_for('leader.list_leaders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi: {e}', 'danger')
    return render_template('admin/add_leader_form.html', title='Thêm Huynh Trưởng & Dự Trưởng', form=form)

@leader_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_leader(user_id):
    user = User.query.get_or_404(user_id)
    form = AddLeaderForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.profile.ho_ten = form.ho_ten.data
        user.profile.ten_thanh = form.ten_thanh.data
        user.profile.sdt = form.sdt.data
        user.profile.dia_chi = form.dia_chi.data
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

@leader_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_leader(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Đã xóa Huynh Trưởng!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi: {e}', 'danger')
    return redirect(url_for('leader.list_leaders'))

@leader_bp.route('/export/xlsx')
@login_required
@admin_required
def export_leaders():
    """Xuất danh sách Huynh trưởng và Dự trưởng ra file Excel."""
    leaders = User.query.filter(User.role.in_(['huynh_truong', 'du_truong'])).join(UserProfile).all()

    if not leaders:
        flash('Không có Huynh trưởng nào để xuất file.', 'info')
        return redirect(url_for('leader.list_leaders'))

    # Tạo dữ liệu
    leader_data = []
    for leader in leaders:
        leader_data.append({
            'Username': leader.username,
            'Email': leader.email,
            'Vai trò': 'Huynh trưởng' if leader.role == 'huynh_truong' else 'Dự trưởng',
            'Họ tên': leader.profile.ho_ten,
            'Tên Thánh': leader.profile.ten_thanh or '',
            'SĐT': leader.profile.sdt or '',
            'Địa chỉ': leader.profile.dia_chi or ''
        })

    df = pd.DataFrame(leader_data)

    # Tạo file Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='DanhSachHuynhTruong')
    writer.close()
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"danh_sach_huynh_truong_{timestamp}.xlsx"
    mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=\"{filename}\""
    response.headers["Content-type"] = mimetype
    return response

# Import từ file
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@leader_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_leaders():
    if request.method == 'POST':
        # === Nút XEM TRƯỚC ===
        if 'preview' in request.form:
            file = request.files.get('file')
            if not file or file.filename == '':
                flash('⚠️ Vui lòng chọn file!', 'warning')
                return redirect(request.url)

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                try:
                    if filename.endswith('.xlsx'):
                        df = pd.read_excel(filepath)
                    else:
                        df = pd.read_csv(filepath)

                    # Lưu đường dẫn file vào session
                    request.session['import_leader_file'] = filepath

                    # Xem trước 5 dòng đầu tiên
                    preview_data = df.head(5).to_html(classes="table table-bordered table-striped table-sm", index=False)
                    return render_template('admin/import_leaders.html', preview=preview_data)

                except Exception as e:
                    flash(f'❌ Lỗi khi đọc file: {e}', 'danger')
                    return redirect(request.url)
            else:
                flash('❌ Chỉ hỗ trợ file .xlsx hoặc .csv!', 'danger')
                return redirect(request.url)

        # === Nút XÁC NHẬN NHẬP ===
        elif 'confirm' in request.form:
            filepath = request.session.get('import_leader_file')
            if not filepath or not os.path.exists(filepath):
                flash('❌ Không tìm thấy file để nhập. Vui lòng tải lại!', 'danger')
                return redirect(request.url)

            try:
                # Đọc lại file
                if filepath.endswith('.xlsx'):
                    df = pd.read_excel(filepath)
                else:
                    df = pd.read_csv(filepath)

                # Chuẩn hóa tên cột
                df.columns = df.columns.str.strip().str.lower()

                added_count = 0

                for _, row in df.iterrows():
                    username = str(row.get("username", "")).strip()
                    email = str(row.get("email", "")).strip()
                    role_str = str(row.get("vai trò", "")).strip()
                    ho_ten = str(row.get("họ tên", "")).strip()
                    ten_thanh = str(row.get("tên thánh", "")).strip()
                    sdt = str(row.get("sđt", "")).strip()
                    dia_chi = str(row.get("địa chỉ", "")).strip()

                    # Bỏ qua dòng thiếu dữ liệu chính
                    if not username or not email or not ho_ten:
                        continue

                    # Chuyển đổi vai trò
                    if role_str.lower() in ['huynh trưởng', 'huynh_truong']:
                        role = 'huynh_truong'
                    elif role_str.lower() in ['dự trưởng', 'du_truong']:
                        role = 'du_truong'
                    else:
                        continue  # Bỏ qua nếu vai trò không hợp lệ

                    # Kiểm tra trùng username hoặc email
                    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                        continue

                    # Tạo user mới
                    new_user = User(
                        username=username,
                        email=email,
                        password='123456',  # Mật khẩu mặc định đơn giản
                        role=role
                    )
                    new_profile = UserProfile(
                        ho_ten=ho_ten,
                        ten_thanh=ten_thanh if ten_thanh else None,
                        sdt=sdt if sdt else None,
                        dia_chi=dia_chi if dia_chi else None
                    )
                    new_user.profile = new_profile

                    db.session.add(new_user)
                    added_count += 1

                db.session.commit()
                flash(f"✅ Đã nhập thành công {added_count} Huynh trưởng/Dự trưởng!", "success")

            except Exception as e:
                db.session.rollback()
                flash(f'❌ Lỗi khi xử lý file: {e}', 'danger')
                return redirect(request.url)

    # GET request
    return render_template('admin/import_leaders.html')
