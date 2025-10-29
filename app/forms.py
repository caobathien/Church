from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, TextAreaField, DateField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from flask_login import current_user
from app.models.user import User
from app.models.student import Student
# --- LỖI ĐÃ SỬA: Import 'ClassModel' thay vì 'Class' ---
from app.models.class_model import ClassModel 
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import datetime

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

# --- FORM LỚP HỌC (Đã sửa lỗi) ---
class ClassForm(FlaskForm):
    name = StringField('Tên lớp học', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Lưu Lớp học')

    def validate_name(self, name):
        class_id = request.view_args.get('class_id')
        # --- LỖI ĐÃ SỬA: Dùng ClassModel ---
        query = ClassModel.query.filter_by(name=name.data)
        if class_id:
            # --- LỖI ĐÃ SỬA: Dùng ClassModel ---
            query = query.filter(ClassModel.id != class_id)
        if query.first():
            raise ValidationError('Tên lớp này đã tồn tại.')

# --- FORM TÌM KIẾM/LỌC SINH VIÊN ---
class SearchStudentForm(FlaskForm):
    search_term = StringField('Tìm kiếm (Tên)', validators=[Optional()])
    # LƯU Ý: choices cho class_filter CẦN được cập nhật động trong route
    # Ví dụ: form.class_filter.choices = [(c.id, c.name) for c in ClassModel.query.all()]
    class_filter = SelectField('Lọc theo lớp', choices=[('', 'Tất cả các lớp')], validators=[Optional()], default='')
    submit_search = SubmitField('Tìm')

# --- STUDENT FORM (Đã cải tiến cho Thiếu Nhi) ---
class StudentForm(FlaskForm):
    """
    Form dùng để Thêm mới hoặc Cập nhật thông tin Thiếu Nhi.
    """
    # --- Thông tin cá nhân ---
    full_name = StringField('Họ và tên',
                            validators=[DataRequired(message="Vui lòng nhập họ tên."),
                                        Length(max=100)])
    ten_thanh = StringField('Tên Thánh',
                            validators=[Optional(),
                                        Length(max=50)])
    date_of_birth = DateField('Ngày sinh (YYYY-MM-DD)',
                            format='%Y-%m-%d',
                                        validators=[DataRequired(message="Vui lòng nhập ngày sinh.")])
    gender = SelectField('Giới tính',
                        choices=[
                            ('Nam', 'Nam'),
                            ('Nữ', 'Nữ'),
                            ('Khác', 'Khác')
                        ],
                        validators=[DataRequired(message="Vui lòng chọn giới tính.")])

    # --- Thông tin phụ huynh ---
    ho_ten_bo = StringField('Họ tên Bố',
                            validators=[Optional(),
                                        Length(max=100)])

    ho_ten_me = StringField('Họ tên Mẹ',
                            validators=[Optional(),
                                        Length(max=100)])

    sdt_phu_huynh = StringField('SĐT Phụ huynh',
                                validators=[Optional(),
                                            Length(max=15)])

    # --- Thông tin lớp học ---
    # Sử dụng QuerySelectField để tự động tải danh sách lớp từ CSDL
    class_obj = QuerySelectField(
        'Lớp',
        query_factory=lambda: ClassModel.query.order_by(ClassModel.name).all(),
        get_label='name',
        allow_blank=True,  # Cho phép để trống (chưa xếp lớp)
        blank_text='-- Chọn lớp --',
        get_pk=lambda obj: obj.id,
        validators=[Optional()] # Lớp là không bắt buộc khi mới thêm
    )

    # --- Điểm số ---
    diem_mieng = FloatField('Điểm miệng (0-10)',
                           validators=[Optional(), NumberRange(min=0, max=10)])
    diem_giua_ki_1 = FloatField('Điểm giữa kì 1 (0-10)',
                               validators=[Optional(), NumberRange(min=0, max=10)])
    diem_cuoi_ki_1 = FloatField('Điểm cuối kì 1 (0-10)',
                               validators=[Optional(), NumberRange(min=0, max=10)])
    diem_giua_ki_2 = FloatField('Điểm giữa kì 2 (0-10)',
                               validators=[Optional(), NumberRange(min=0, max=10)])
    diem_cuoi_ki_2 = FloatField('Điểm cuối kì 2 (0-10)',
                               validators=[Optional(), NumberRange(min=0, max=10)])

    submit = SubmitField('Lưu thông tin')


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
    avatar = FileField('Ảnh đại diện', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ chấp nhận file ảnh!')
    ])
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

class SearchUserForm(FlaskForm):
    search_term = StringField('Tìm kiếm (Tên đăng nhập hoặc Email)', validators=[Optional()])
    role_filter = SelectField('Lọc theo vai trò', choices=[
        ('', 'Tất cả vai trò'),
        ('guest', 'Khách'),
        ('huynh_truong', 'Huynh Trưởng'),
        ('du_truong', 'Dự Trưởng'),
        ('admin', 'Admin')
    ], validators=[Optional()], default='')
    submit_search = SubmitField('Tìm')

class AdminUpdateUserForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # --- LỖI ĐÃ SỬA: Cập nhật đầy đủ vai trò ---
    role = SelectField('Vai trò', 
                    choices=[
                        ('guest', 'Khách'), 
                        ('huynh_truong', 'Huynh Trưởng'), 
                        ('du_truong', 'Dự Trưởng'), 
                        ('admin', 'Admin')
                    ], 
                    validators=[DataRequired()])
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
                
class AddLeaderForm(FlaskForm):
    # --- Trường cho Model User (Đăng nhập) ---
    username = StringField('Tên đăng nhập', 
        validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', 
        validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', 
        validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận Mật khẩu', 
        validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Vai trò', 
                    choices=[
                        ('huynh_truong', 'Huynh Trưởng'), 
                        ('du_truong', 'Dự Trưởng')
                    ], 
                    validators=[DataRequired(message="Vui lòng chọn vai trò.")])
    # --- Trường cho Model UserProfile (Thông tin cá nhân) ---
    ho_ten = StringField('Họ và Tên', 
        validators=[DataRequired(), Length(max=100)])
    ten_thanh = StringField('Tên Thánh', 
        validators=[Optional(), Length(max=50)])
    sdt = StringField('Số điện thoại', 
        validators=[Optional(), Length(max=15)])
    dia_chi = StringField('Địa chỉ', 
        validators=[Optional(), Length(max=255)])
    
    submit = SubmitField('Tạo Tài Khoản')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên đăng nhập này đã tồn tại.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email này đã tồn tại.')

class AttendanceForm(FlaskForm):
    """
    Form để điểm danh cho một lớp trong một ngày cụ thể.
    """
    date = DateField('Ngày điểm danh', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.utcnow().date)
    submit = SubmitField('Điểm danh')

class BulkAttendanceForm(FlaskForm):
    """
    Form để cập nhật điểm danh hàng loạt cho nhiều học sinh.
    """
    submit = SubmitField('Lưu điểm danh')
