from app import db
from datetime import datetime

class Attendance(db.Model):
    """
    Model Attendance: Đại diện cho việc điểm danh của thiếu nhi.
    """
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)

    # Liên kết với Student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    # Liên kết với Class (để dễ lọc theo lớp)
    class_id = db.Column(db.Integer, db.ForeignKey('class_model.id'), nullable=False)

    # Ngày điểm danh
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)

    # Trạng thái điểm danh: 'present', 'absent', 'late'
    status = db.Column(db.String(20), nullable=False, default='present')

    # Người thực hiện điểm danh (Admin hoặc Huynh trưởng)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Thời gian tạo
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref='attendances')
    class_assigned = db.relationship('ClassModel', backref='attendances')
    creator = db.relationship('User', backref='created_attendances')

    # Đảm bảo mỗi học sinh chỉ được điểm danh một lần mỗi ngày trong một lớp
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_id', 'date', name='unique_student_class_date'),
    )

    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, class_id={self.class_id}, date={self.date}, status='{self.status}')>"
