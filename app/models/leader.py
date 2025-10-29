from app import db

class Leader(db.Model):
    __tablename__ = 'leader'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    position = db.Column(db.String(50), nullable=False)  # 'huynh_truong' or 'du_truong'
    
    user = db.relationship('User', backref='leader')
    
    def __repr__(self):
        return f"<Leader(id={self.id}, user_id={self.user_id}, position='{self.position}')>"
