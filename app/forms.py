from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from flask_login import current_user
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from wtforms_sqlalchemy.fields import QuerySelectField

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

# --- FORM MỚI CHO LỚP HỌC ---
class ClassForm(FlaskForm):
    name = StringField('Tên lớp học', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Lưu Lớp học')

    def validate_name(self, name):
        class_id = request.view_args.get('class_id')
        query = Class.query.filter_by(name=name.data)
        if class_id:
            query = query.filter(Class.id != class_id)
        if query.first():
            raise ValidationError('Tên lớp này đã tồn tại.')

# --- FORM TÌM KIẾM/LỌC SINH VIÊN ---
class SearchStudentForm(FlaskForm):
    search_term = StringField('Tìm kiếm (Tên hoặc Mã SV)', validators=[Optional()])
    class_filter = SelectField('Lọc theo lớp', choices=[('', 'Tất cả các lớp')], validators=[Optional()], default='')
    submit_search = SubmitField('Tìm')

# --- STUDENT FORM (Đã sửa lỗi) ---
class StudentForm(FlaskForm):
    student_code = StringField('Mã sinh viên', validators=[DataRequired(), Length(min=5, max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(min=5, max=100)])
    date_of_birth = DateField('Ngày sinh', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')], validators=[DataRequired()])
    
    # <-- LỖI ĐÃ ĐƯỢC SỬA Ở ĐÂY -->
    # Đã thay thế trường 'class_name' bằng dropdown 'class_obj'
    class_obj = QuerySelectField('Lớp', 
                               query_factory=lambda: Class.query.order_by(Class.name).all(), 
                               get_label='name', 
                               allow_blank=False,
                               validators=[DataRequired(message="Vui lòng chọn lớp.")])

    gpa = FloatField('Điểm trung bình', validators=[DataRequired(), NumberRange(min=0.0, max=4.0, message="Điểm phải từ 0.0 đến 4.0")])
    submit = SubmitField('Lưu thông tin')

    def validate_student_code(self, student_code):
        student_id = request.view_args.get('student_id')
        query = Student.query.filter_by(student_code=student_code.data)
        if student_id:
            query = query.filter(Student.id != student_id)
        if query.first():
            raise ValidationError('Mã sinh viên này đã tồn tại. Vui lòng chọn mã khác.')

# --- CÁC FORM KHÁC (Không thay đổi) ---
class AnnouncementForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    image = FileField('Ảnh minh họa (Tùy chọn)', validators=[
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