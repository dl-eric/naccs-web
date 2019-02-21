from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo

def esea_validate(form, field):
    mesg = "Enter a valid ESEA page URL"

    def _validate(form, field):
        esea = str(field.data)

        if not 'play.esea.net/users/' in esea:
            raise ValidationError(mesg)
    
    return _validate(form, field)

def verify_pass(form, field, pw=''):

    def _validate(form, field):
        if field.data != pw:
            raise ValidationError("Passwords must match")
    return _validate(form, field)

def password_validate(form, field):
    len_mesg = "Your password must be at least 8 characters long."
    format_mesg = "Your password must consist of at least one lowercase letter, uppercase letter, and number"

    def _validate(form, field):
        pw = str(field.data)

        if len(pw) < 8:
            raise ValidationError(len_mesg)
        else:
            has_numbers = False
            has_upper = False 
            has_lower = False
            for i in range(len(pw)):
                c = pw[i]
                if not has_numbers and c.isnumeric():
                    has_numbers = True
                elif not has_upper and c.isupper():
                    has_upper = True 
                elif not has_lower and c.islower():
                    has_lower = True
            if not has_numbers or not has_upper or not has_lower:
                raise ValidationError(format_mesg)

    return _validate(form, field)

def email_validate(form, field):
    message = "You must use a .edu or .ca address"

    def _suffix_validator(field, suffix):
        return len(field) >= len(suffix) and field[len(field)-len(suffix):].lower() == suffix

    def _validate(form, field):
        email = str(field.data)

        is_edu = _suffix_validator(email, 'edu')
        is_ca = _suffix_validator(email, 'ca')
        print(is_edu, is_ca)
        if not is_edu and not is_ca:
            raise ValidationError(message)

    return _validate(form, field)

def discord_validate(form, field):
    format_mesg = "Discord must have the format <name>#<numbers>. E.g pie-#8509"
    exist_mesg = "Unable to find user. Discord account must exist!"

    def _check_user_exists(user):
        return True

    def _validate(form, field):
        parts = str(field.data).split('#')

        if len(parts) != 2: # Check if there exists one '#'
            raise ValidationError(format_mesg)

        elif not parts[1].isnumeric(): #
            print(parts[1])
            raise ValidationError(format_mesg)
        elif not _check_user_exists(field.data):
            raise ValidationError(exist_mesg)
    return _validate(form, field)

class RegisterForm(FlaskForm):
    username =  StringField("Username", validators=[DataRequired()], render_kw={'class': 'input', 'placeholder': ' '})
    email =     StringField("Email", validators=[DataRequired(), Email(), email_validate], render_kw={'class': 'input', 'placeholder': ' '})
    password =  PasswordField("Password", validators=[DataRequired(), password_validate], render_kw={'class': 'input', 'placeholder': ' '})
    verify_pass = PasswordField("Confirm Password", validators=[EqualTo('password', message="Passwords must match")], render_kw={'class': 'input', 'placeholder': ' '})
    discord =   StringField("Discord", validators=[DataRequired(), discord_validate], render_kw={'class': 'input', 'placeholder': ' '})
    esea =      StringField("ESEA Profile", validators=[DataRequired(), esea_validate], render_kw={'class': 'input', 'placeholder': ' '})
    submit =    SubmitField()

class VerificationForm(FlaskForm):
    code    = StringField("Verification Code")
    submit  = SubmitField()

class SignInForm(FlaskForm):
    email_or_username       = StringField("E-mail or Username", validators=[DataRequired()], render_kw={'class': 'input', 'placeholder': ' '})
    password                = PasswordField("Password", validators=[DataRequired()], render_kw={'class': 'input', 'placeholder': ' '})
    submit                  = SubmitField()

class ProfileForm(FlaskForm):
    discord     = StringField(validators=[DataRequired(), discord_validate])
    submit      = SubmitField("Change Profile")