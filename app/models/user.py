from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

class_leaders_association = db.Table('class_leaders_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class_model.id'), primary_key=True)
)


@login_manager.user_loader
def load_user(user_id):
    """Callback bắt buộc của Flask-Login để tải người dùng từ session."""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    Model User: Chịu trách nhiệm cho việc xác thực, phân quyền 
    và liên kết tới các model khác.
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    
    # Các vai trò: 'guest', 'huynh_truong', 'du_truong', 'admin'
    role = db.Column(db.String(50), nullable=False, default='guest')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # --- Mối quan hệ ---
    profile = db.relationship(
        'UserProfile', 
        back_populates='user', 
        uselist=False, 
        cascade='all, delete-orphan'
    )

    # 2. Liên kết Nhiều-Nhiều với ClassModel (Các lớp được phân công)
    assigned_classes = db.relationship(
        'ClassModel', 
        secondary=class_leaders_association,
        back_populates='leaders', 
        lazy='dynamic'
    )

    # 3. Các liên kết Một-Nhiều khác (ví dụ: thông báo, phản hồi)
    announcements = db.relationship('Announcement', backref='author', lazy=True)
    feedbacks = db.relationship('Feedback', backref='sender', lazy=True)


    # --- Phương thức xử lý mật khẩu ---
    @property
    def password(self):
        """Ngăn chặn việc đọc trực tiếp mật khẩu."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password_text):
        """Tự động hash mật khẩu khi gán."""
        self.password_hash = bcrypt.generate_password_hash(password_text).decode('utf-8')

    def verify_password(self, password_text):
        """Kiểm tra mật khẩu người dùng nhập vào."""
        return bcrypt.check_password_hash(self.password_hash, password_text)

    # --- Phương thức hỗ trợ phân quyền ---
    def is_admin(self):
        """Kiểm tra có phải Admin không."""
        return self.role == 'admin'

    def is_leader(self):
        """
        Kiểm tra có phải là Lãnh đạo (Huynh trưởng hoặc Dự trưởng) không.
        Dùng hàm này trong decorator sẽ linh hoạt hơn.
        """
        return self.role in ('huynh_truong', 'du_truong')

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"