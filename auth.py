import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from warrant import Cognito
from warrant.aws_srp import AWSSRP
from forms import RegisterForm, VerificationForm, SignInForm
import boto3

AWS_COGNITO_POOL_ID = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID = os.environ.get('AWS_COGNITO_CLIENT_ID')
AWS_COGNITO_ACCESS_KEY = os.environ.get('AWS_COGNITO_ACCESS_KEY')
AWS_COGNIRO_SECRET_KEY = os.environ.get('AWS_COGNITO_SECRET_KEY')

auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID)

auth_page = Blueprint('auth_page', __name__, template_folder='templates')

# Uses boto3 to add a 'username' to 'groupname'
def add_user_to_group(username, groupname):
    boto3_client_kwargs = {'aws_access_key_id': AWS_COGNITO_ACCESS_KEY, 'aws_secret_access_key': AWS_COGNIRO_SECRET_KEY}
    boto3_client = boto3.client('cognito-idp', **boto3_client_kwargs)
    add_user_to_group_kwargs = {'UserPoolId': AWS_COGNITO_POOL_ID, 'Username': username, 'GroupName': groupname}
    boto3_client.admin_add_user_to_group(**add_user_to_group_kwargs)

@auth_page.route('/user')
def user():
    if 'access_token' not in session:
        return redirect(url_for('index'))
        
    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=session.get('username'), access_token=session.get('access_token'))
    user = auth.get_user(attr_map={"custom:discord":"discord", "custom:esea":"esea"})
    
    return render_template('user.html', user=user)

@auth_page.route('/signin', methods=['post', 'get'])
def signin():
    if 'access_token' in session:
        # We're already logged in!
        return redirect(url_for('index'))

    form = SignInForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=username, access_key='dummy', secret_key='dummy')
    
        try: 
            auth.authenticate(password)
        except auth.client.exceptions.UserNotFoundException:
            flash("Username not found")
            return render_template('signin.html', form=form)
        except auth.client.exceptions.NotAuthorizedException:
            flash("Username or password is incorrect")
            return render_template('signin.html', form=form)
        except auth.client.exceptions.UserNotConfirmedException:
            session['verify'] = True
            return redirect(url_for('auth_page.verification'))

        session['username'] = username
        session['access_token'] = auth.access_token
        session['id_token'] = auth.id_token
        session['refresh_token'] = auth.refresh_token
        return redirect(url_for('index'))
    return render_template('signin.html', form=form)

@auth_page.route('/signout')
def signout():
    if 'access_token' in session:
        session.pop('username', None)
        session.pop('access_token', None)
        session.pop('id_token', None)
        session.pop('refresh_token', None)
    return redirect(url_for('index'))

@auth_page.route('/verification', methods=['post', 'get'])
def verification():
    if 'verify' not in session:
        return redirect(url_for('index'))

    form = VerificationForm()

    if form.validate_on_submit():
        code = form.code.data
        try:
            auth.confirm_sign_up(code, username=session.get('username', None))
        except auth.client.exceptions.CodeMismatchException:
            flash("Invalid or expired Code")
            return render_template('verification.html', form=form)
        except auth.client.exceptions.AliasExistsException:
            flash("Email already exists")
            return render_template('verification.html', form=form)
        except auth.client.exceptions.NotAuthorizedException:
            flash("The email associated with this account has already been verified by another account")
            return render_template('verification.html', form=form)

        session.pop('verify', None)
        flash("You've been verified!")
        return redirect(url_for('auth_page.signin')) # TODO: Add success message!
    return render_template('verification.html', form=form)

@auth_page.route('/register', methods=['post', 'get'])
def register():
    if 'access_token' in session:
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
            session['username'] = username
            add_user_to_group(username, 'NotInDiscord')
        except auth.client.exceptions.UsernameExistsException:
            flash("Username already exists")
            return render_template('register.html', form=form)

        session['verify'] = True
        return redirect(url_for('auth_page.verification'))

    return render_template('register.html', form=form)
