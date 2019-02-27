import os
import functools
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from warrant import Cognito
from warrant.aws_srp import AWSSRP
from forms import RegisterForm, VerificationForm, SignInForm, ProfileForm, email_validate
import boto3

AWS_COGNITO_POOL_ID     = os.environ.get('AWS_COGNITO_POOL_ID')
AWS_COGNITO_CLIENT_ID   = os.environ.get('AWS_COGNITO_CLIENT_ID')
AWS_IAM_ACCESS_KEY      = os.environ.get('AWS_IAM_ACCESS_KEY')
AWS_IAM_SECRET_KEY      = os.environ.get('AWS_IAM_SECRET_KEY')

auth_page = Blueprint('auth_page', __name__, template_folder='templates')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'access_token' not in session:
            return redirect(url_for('auth_page.signin'))

        return view(**kwargs)

    return wrapped_view

def is_email(input):
    if '@' not in input:
        return False 

    def _suffix_validator(field, suffix):
        return len(field) >= len(suffix) and field[len(field)-len(suffix):].lower() == suffix

    def _validate(input):
        is_edu = _suffix_validator(input, 'edu')
        is_ca = _suffix_validator(input, 'ca')
        
        if not is_edu and not is_ca:
            return False
        return True
    return _validate(input)

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')

# Uses boto3 to add a 'username' to 'groupname'
def add_user_to_group(username, groupname):
    boto3_client_kwargs = {'aws_access_key_id': AWS_IAM_ACCESS_KEY, 'aws_secret_access_key': AWS_IAM_SECRET_KEY}
    boto3_client = boto3.client('cognito-idp', **boto3_client_kwargs)
    add_user_to_group_kwargs = {'UserPoolId': AWS_COGNITO_POOL_ID, 'Username': username, 'GroupName': groupname}
    boto3_client.admin_add_user_to_group(**add_user_to_group_kwargs)

@auth_page.route('/user', methods=['post', 'get'])
@login_required
def user():
    id_token        = session.get('id_token')
    refresh_token   = session.get('refresh_token')
    access_token    = session.get('access_token')
    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, id_token=id_token, refresh_token=refresh_token, access_token=access_token)
    form = ProfileForm()

    # Renew tokens if expired
    try:
        # Renew = Flase because I don't think the library one works.
        if auth.check_token(renew=False):
            auth_params = {'REFRESH_TOKEN': refresh_token}
            response = auth.client.initiate_auth(ClientId=AWS_COGNITO_CLIENT_ID, AuthFlow='REFRESH_TOKEN', AuthParameters=auth_params)
            session['id_token']         = response['AuthenticationResult']['IdToken']
            session['access_token']     = response['AuthenticationResult']['AccessToken']
    except Exception as e:
        # Something went wrong. Log out the user.
        return redirect(url_for('auth_page.signout'))
    
    if form.validate_on_submit():
        discord = form.discord.data 
        
        try:
            auth.update_profile({'custom:discord':discord}, attr_map=dict())
            flash('Sucessfully changed profile settings!', 'success')
        except:
            flash("Something went wrong.", "error")
    else:
        flash_errors(form)
    user = auth.client.get_user(AccessToken=session.get('access_token'))
    user = auth.get_user_obj(username=user['Username'], attribute_list=user['UserAttributes'], attr_map={"custom:discord":"discord", "custom:esea":"esea"})
    form.discord.data = user.discord

    return render_template('user.html', user=user, username=session.get('username'), form=form)

@auth_page.route('/signin', methods=['post', 'get'])
def signin():
    if 'access_token' in session:
        # We're already logged in!
        return redirect(url_for('index'))

    form = SignInForm()
    if form.validate_on_submit():
        email_or_username = str(form.email_or_username.data)
        if is_email(email_or_username):
            email_or_username = email_or_username.lower()

        password = form.password.data

        auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=email_or_username, access_key='dummy', secret_key='dummy')
    
        try: 
            auth.authenticate(password)
        except auth.client.exceptions.UserNotFoundException:
            if is_email(email_or_username):
                flash("User not found. If you haven't verified your account yet, please log in with your username.", 'error')
            else: 
                flash("User not found.", 'error')
            return render_template('signin.html', form=form)
        except auth.client.exceptions.NotAuthorizedException:
            flash("E-mail or password is incorrect", 'error')
            return render_template('signin.html', form=form)
        except auth.client.exceptions.UserNotConfirmedException:
            session['verify'] = True
            session['username'] = email_or_username
            return redirect(url_for('auth_page.verification'))
        
        user = auth.client.get_user(AccessToken=auth.access_token)
        session['username'] = user['Username']
        session['access_token'] = auth.access_token
        session['id_token'] = auth.id_token
        session['refresh_token'] = auth.refresh_token
        session.permanent = True # 31 days until cookie expires
        return redirect(url_for('index'))
    else:
        flash_errors(form)
    return render_template('signin.html', form=form)

@auth_page.route('/signout')
@login_required
def signout():
    session.pop('username', None)
    session.pop('access_token', None)
    session.pop('id_token', None)
    session.pop('refresh_token', None)
    return redirect(url_for('index'))

@auth_page.route('/verification', methods=['post', 'get'])
def verification():
    if 'verify' not in session:
        return redirect(url_for('index'))

    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=session.get('username'))

    form = VerificationForm()

    if request.method == 'POST' and request.form.get('resend') == 'Resend E-Mail':
        flash ("Check your e-mail for the new verification code.", 'success')
        auth.client.resend_confirmation_code(ClientId=AWS_COGNITO_CLIENT_ID, Username=session.get('username'))
        session['re-sent'] = True
        return render_template('verification.html', form=form, resent=session.get('re-sent', False))

    if form.validate_on_submit():
        code = form.code.data
        try:
            auth.confirm_sign_up(code, username=session.get('username'))
        except auth.client.exceptions.CodeMismatchException:
            flash("Invalid or expired Code", 'error')
            return render_template('verification.html', form=form)
        except auth.client.exceptions.AliasExistsException:
            flash("Email already exists", 'error')
            return render_template('verification.html', form=form)
        except auth.client.exceptions.NotAuthorizedException:
            flash("The email associated with this account has already been verified by another account", 'error')
            return render_template('verification.html', form=form)

        session.pop('verify', None)
        session.pop('re-sent', None)
        flash("You've been verified!", 'success')
        return redirect(url_for('auth_page.signin'))
    return render_template('verification.html', form=form, resent=session.get('re-sent', False))

@auth_page.route('/register', methods=['post', 'get'])
def register():
    if 'access_token' in session:
        # We're already logged in!
        return redirect(url_for('index'))

    auth = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username='dummy', access_key='dummy', secret_key='dummy')

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = str(form.email.data).lower()
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
            flash("Username already exists", 'error')
            return render_template('register.html', form=form)
        except auth.client.exceptions.InvalidParameterException:
            flash("Username cannot be an e-mail", 'error')
            return render_template('register.html', form=form)
        except Exception as e:
            flash("Something went wrong. Double check your parameters and try again.", 'error')
            return render_template('register.html', form=form)
        
        session['verify'] = True
        return redirect(url_for('auth_page.verification'))
    else:
        flash_errors(form)

    return render_template('register.html', form=form)
