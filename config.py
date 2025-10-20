import os

class Config:
    # Khóa bí mật cho Flask-WTF (form validation)
    SECRET_KEY = 'supersecretkey'

    # Đường dẫn tới database (SQLite)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'students.db')

    # Tắt cảnh báo không cần thiết
    SQLALCHEMY_TRACK_MODIFICATIONS = False
