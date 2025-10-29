import os

# Lấy đường dẫn tuyệt đối của thư mục chứa file config.py
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Lớp cấu hình cơ bản cho ứng dụng.
    """
    # Khóa bí mật để bảo vệ session và form
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ban-nen-thay-doi-key-nay'
    
    # Cấu hình SQLAlchemy
    # Tắt tính năng theo dõi sự thay đổi không cần thiết để tiết kiệm tài nguyên
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình đường dẫn tới database SQLite
    # Sử dụng os.path.join để đảm bảo tương thích trên các hệ điều hành
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'students.db')
    
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'img')
