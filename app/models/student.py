from app import db
from datetime import datetime

class Student(db.Model):
    """
    Model Student: Đại diện cho thiếu nhi trong CSDL.
    """
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # --- Thông tin cá nhân ---
    ten_thanh = db.Column(db.String(50), nullable=True) # Tên Thánh (Tùy chọn)
    full_name = db.Column(db.String(100), nullable=False) # Họ và Tên
    date_of_birth = db.Column(db.Date, nullable=False) # Ngày sinh
    gender = db.Column(db.String(10), nullable=False) # Giới tính ('Nam', 'Nữ')

    # --- Thông tin liên hệ Phụ huynh (rất cần thiết cho quản lý) ---
    ho_ten_bo = db.Column(db.String(100), nullable=True)
    ho_ten_me = db.Column(db.String(100), nullable=True)
    sdt_phu_huynh = db.Column(db.String(15), nullable=True)
    
    # --- Liên kết Lớp (Nhiều-Một) ---
    # Một thiếu nhi sẽ thuộc về một lớp.
    # 'class_model.id' phải khớp với __tablename__ của ClassModel
    # nullable=True: Cho phép tạo thiếu nhi trước, xếp lớp sau.
    class_id = db.Column(db.Integer, db.ForeignKey('class_model.id'), nullable=True)

    # --- Điểm số ---
    # Điểm miệng (0-10)
    diem_mieng = db.Column(db.Float, nullable=True, default=0.0)

    # Điểm giữa kì 1 (0-10)
    diem_giua_ki_1 = db.Column(db.Float, nullable=True, default=0.0)

    # Điểm cuối kì 1 (0-10)
    diem_cuoi_ki_1 = db.Column(db.Float, nullable=True, default=0.0)

    # Điểm giữa kì 2 (0-10)
    diem_giua_ki_2 = db.Column(db.Float, nullable=True, default=0.0)

    # Điểm cuối kì 2 (0-10)
    diem_cuoi_ki_2 = db.Column(db.Float, nullable=True, default=0.0)

    @property
    def diem_tong(self):
        """Tính điểm tổng: (điểm miệng + giữa kì 1 + cuối kì 1 + giữa kì 2 + cuối kì 2) / 5"""
        scores = [self.diem_mieng or 0, self.diem_giua_ki_1 or 0, self.diem_cuoi_ki_1 or 0,
                 self.diem_giua_ki_2 or 0, self.diem_cuoi_ki_2 or 0]
        return round(sum(scores) / 5, 2) if any(scores) else 0.0

    def __repr__(self):
        # 'class_assigned' là backref từ ClassModel
        class_name = self.class_assigned.name if self.class_assigned else 'Chưa xếp lớp'
        return f"<Student(id={self.id}, name='{self.full_name}', class='{class_name}')>"