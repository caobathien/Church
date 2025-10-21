from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models.announcement import Announcement
from app.models.feedback import Feedback
from app.forms import AnnouncementForm
import secrets
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- HÀM HỖ TRỢ LƯU ẢNH ---
def save_picture(form_picture):
    # Tạo một tên file ngẫu nhiên để tránh trùng lặp
    random_hex = secrets.token_hex(8)
    # Lấy đuôi file (ví dụ: .jpg)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # Lấy đường dẫn tuyệt đối đến thư mục uploads
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    
    # Lưu ảnh
    form_picture.save(picture_path)
    
    return picture_fn # Trả về tên file mới

@admin_bp.route('/announcement/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        image_file = None
        # 3. KIỂM TRA NẾU CÓ FILE TẢI LÊN
        if form.image.data:
            image_file = save_picture(form.image.data)
            
        # 4. LƯU TÊN ẢNH VÀO DATABASE
        announcement = Announcement(
            title=form.title.data, 
            content=form.content.data, 
            author=current_user,
            image_filename=image_file # <-- Thêm tên file vào
        )
        db.session.add(announcement)
        db.session.commit()
        flash('Thông báo đã được đăng!', 'success')
        return redirect(url_for('main.home'))
    return render_template('admin/announcement_form.html', title='Tạo thông báo', form=form)

@admin_bp.route('/feedback')
@login_required
@admin_required
def view_feedback():
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin/feedback_list.html', title='Danh sách Phản hồi', feedbacks=feedbacks)

@admin_bp.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Phản hồi đã được xóa.', 'success')
    return redirect(url_for('admin.view_feedback'))

@admin_bp.route('/announcement/<int:announcement_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(announcement_id):
    """Xử lý việc xóa một thông báo."""
    ann = Announcement.query.get_or_404(announcement_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Thông báo đã được xóa thành công.', 'success')
    return redirect(url_for('main.home'))