from app import db
from app.models.user import class_leaders_association

class ClassModel(db.Model):
    # Tên bảng trong CSDL (quan trọng: phải khớp với ForeignKey ở trên)
    __tablename__ = 'class_model'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    students = db.relationship('Student', backref='class_assigned', lazy='dynamic')
    leaders = db.relationship(
        'User',
        secondary=class_leaders_association,
        back_populates='assigned_classes',
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<ClassModel(id={self.id}, name='{self.name}')>"
