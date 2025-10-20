from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import admin_required
from app.models.announcement import Announcement
from app.models.feedback import Feedback
from app.forms import AnnouncementForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/announcement/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data, author=current_user)
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