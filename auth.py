import os
from flask import Blueprint, render_template
from warrant import Cognito

AWS_COGNITO_POOL_ID = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')

auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID)

auth_page = Blueprint('auth_page', __name__, template_folder='templates')

@auth_page.route('/signin')
def signin():
    return render_template('signin.html')

@auth_page.route('/register')
def register():
    return render_template('register.html')
