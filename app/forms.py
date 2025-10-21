from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models.user import User
from app.models.student import Student
from wtforms.validators import EqualTo, ValidationError
from flask_login import current_user
from app.models.user import User
from flask_wtf.file import FileField, FileAllowed, DataRequired

class RegistrationForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email này đã tồn tại. Vui lòng chọn email khác.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')
    
class StudentForm(FlaskForm):
    student_code = StringField('Mã sinh viên', validators=[DataRequired(), Length(min=5, max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(min=5, max=100)])
    date_of_birth = DateField('Ngày sinh', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[DataRequired()])
    class_name = StringField('Lớp', validators=[DataRequired(), Length(max=50)])
    gpa = FloatField('Điểm trung bình', validators=[DataRequired(), NumberRange(min=0.0, max=4.0, message="Điểm phải từ 0.0 đến 4.0")])
    submit = SubmitField('Lưu thông tin')

    def validate_student_code(self, student_code):
        student_id = request.view_args.get('student_id')
        query = Student.query.filter_by(student_code=student_code.data)
        if student_id:
            query = query.filter(Student.id != student_id)
        if query.first():
            raise ValidationError('Mã sinh viên này đã tồn tại. Vui lòng chọn mã khác.')

class AnnouncementForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Nội dung', validators=[DataRequired()])

    image = FileField('Ảnh minh họa (Bắt buộc)', validators=[
        DataRequired(message="Vui lòng chọn một ảnh để tải lên."), 
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ chấp nhận file ảnh!')
    ])

    submit = SubmitField('Đăng thông báo')

class FeedbackForm(FlaskForm):
    content = TextAreaField('Nội dung phản hồi', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gửi phản hồi')

class UpdateAccountForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Cập nhật')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email này đã tồn tại. Vui lòng chọn email khác.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Đổi mật khẩu')

class AdminUpdateUserForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Vai trò', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Cập nhật')

    # Cần user_id để kiểm tra validation
    def __init__(self, user, *args, **kwargs):
        super(AdminUpdateUserForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_username(self, username):
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Tên đăng nhập này đã tồn tại.')

    def validate_email(self, email):
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email này đã tồn tại.')