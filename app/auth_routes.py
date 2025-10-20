from flask import Blueprint
from app.controllers import auth_controller

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return auth_controller.login()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    return auth_controller.register()

@auth.route('/logout')
def logout():
    return auth_controller.logout()
