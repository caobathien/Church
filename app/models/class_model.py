from app import db

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Mối quan hệ: Một Class có nhiều Student
    # backref='class_rel' tạo thuộc tính student.class_rel để truy cập Class từ Student
    students = db.relationship('Student', backref='class_rel', lazy=True)

    def __repr__(self):
        return f"Class('{self.name}')"