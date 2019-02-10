import os
from flask import Blueprint, render_template, request, redirect, url_for
from warrant import Cognito
from forms import RegisterForm, VerificationForm

AWS_COGNITO_POOL_ID = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')

auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID)

auth_page = Blueprint('auth_page', __name__, template_folder='templates')

cognito_user = ""

@auth_page.route('/user')
def user():
    return render_template('user.html')

@auth_page.route('/signin', methods=['post', 'get'])
def signin():
    return render_template('signin.html')

@auth_page.route('/verification', methods=['post', 'get'])
def verification():
    form = VerificationForm()
    if form.validate_on_submit():
        code = form.code.data
        try:
            auth.confirm_sign_up(code, username=cognito_user)
        except:
            pass # TODO
        return redirect(url_for('auth_page.signin')) # TODO: Add success message!
    return render_template('verification.html', form=form)

@auth_page.route('/register', methods=['post', 'get'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        discord = form.discord.data
        esea = form.esea.data
        
        auth.add_base_attributes(email=email)
        auth.add_custom_attributes(discord=discord, esea=esea)

        try:
            auth.register(username, password)
            cognito_user = username
        except auth.client.exceptions.UsernameExistsException:
            pass # TODO

        return redirect(url_for('auth_page.verification'))

    return render_template('register.html', form=form)
