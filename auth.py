import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from warrant import Cognito
from forms import RegisterForm, VerificationForm, SignInForm

AWS_COGNITO_POOL_ID = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')

auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID)

auth_page = Blueprint('auth_page', __name__, template_folder='templates')

@auth_page.route('/user')
def user():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('user.html')

@auth_page.route('/signin', methods=['post', 'get'])
def signin():
    if 'username' in session:
        # We're already logged in!
        return redirect(url_for('index'))
        
    form = SignInForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=username)
        
        try: 
            auth.authenticate(password)
        except auth.client.exceptions.UserNotFoundException:
            pass # TODO
        except auth.client.exceptions.InvalidPasswordException:
            pass # TODO
        except:
            pass # TODO

        # TODO: Check if account needs verification. If so, redirect to verification
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('signin.html', form=form)

@auth_page.route('/signout')
def signout():
    session.pop('username', None)
    return redirect(url_for('index'))

@auth_page.route('/verification', methods=['post', 'get'])
def verification():
    if 'verify' not in session:
        return redirect(url_for('index'))

    form = VerificationForm()
    if form.validate_on_submit():
        code = form.code.data
        try:
            auth.confirm_sign_up(code, username=session.get('curr_username', None))
        except:
            pass # TODO

        session.pop('verify', None)
        return redirect(url_for('auth_page.signin')) # TODO: Add success message!
    return render_template('verification.html', form=form)

@auth_page.route('/register', methods=['post', 'get'])
def register():
    if 'username' in session:
        # We're already logged in!
        return redirect(url_for('index'))

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
            session['curr_username'] = username
        except auth.client.exceptions.UsernameExistsException:
            pass # TODO

        session['verify'] = True
        return redirect(url_for('auth_page.verification'))

    return render_template('register.html', form=form)
