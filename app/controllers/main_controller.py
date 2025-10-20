from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.announcement import Announcement
from app.models.feedback import Feedback
from app.forms import FeedbackForm

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=['GET', 'POST'])
@login_required
def home():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(content=form.content.data, sender=current_user)
        db.session.add(feedback)
        db.session.commit()
        flash('Phản hồi của bạn đã được gửi. Cảm ơn bạn!', 'success')
        return redirect(url_for('main.home'))

    # Lấy tất cả thông báo, sắp xếp mới nhất lên đầu
    announcements = Announcement.query.order_by(Announcement.timestamp.desc()).all()
    return render_template('home.html', title="Trang chủ", announcements=announcements, form=form)