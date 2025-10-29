from app import db

class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    id = db.Column(db.Integer, primary_key=True)

    # Các trường thông tin cá nhân bạn yêu cầu
    ten_thanh = db.Column(db.String(50), nullable=True)
    ho_ten = db.Column(db.String(100), nullable=False)
    sdt = db.Column(db.String(15), nullable=True)
    dia_chi = db.Column(db.String(255), nullable=True)

    # Trường avatar (tên file ảnh)
    avatar_filename = db.Column(db.String(100), nullable=True)

    # --- Liên kết Một-Một với Model User ---
    # 'user.id' là tên bảng 'user' và cột 'id'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    # Mối quan hệ ngược lại (để từ UserProfile có thể .user)
    user = db.relationship('User', back_populates='profile')

    def __repr__(self):
        return f"<UserProfile(ho_ten='{self.ho_ten}')>"
