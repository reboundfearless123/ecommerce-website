from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from property.models import Registertable
from flask_wtf.file import FileField,FileAllowed

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField("Email", validators=[DataRequired(), Length(min=6), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user_exists = Registertable.query.filter_by(username=username.data).first()
        if user_exists:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        email_exists = Registertable.query.filter_by(email=email.data).first()
        if email_exists:
            raise ValidationError('Email address already registered.')
        
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=6), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")



class RequestResetForm(FlaskForm):
    email=StringField('email',validators=[DataRequired(),Email()])
    submit=SubmitField('Request Reset Password')
    def validate_email(self, email):
        email_exists = Registertable.query.filter_by(email=email.data).first()
        if email_exists is None:
            raise ValidationError('No account with that email found ')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), Length(min=8), EqualTo('password')])
    submit=SubmitField('Reset Password')
