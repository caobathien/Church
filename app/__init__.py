from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
import os
from flask_ckeditor import CKEditor

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
bootstrap = Bootstrap()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    # Đăng ký Blueprints
    from app.controllers.main_controller import main_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.student_controller import student_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.account_controller import account_bp
    from app.controllers.class_controller import class_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(class_bp)

    with app.app_context():
        # Import models để SQLAlchemy có thể tạo bảng
        from app.models import user, student, announcement, feedback, class_model
        db.create_all()

    return app