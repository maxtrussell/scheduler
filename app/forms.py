from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    IntegerField,
)
from wtforms.validators import (
    Email,
    EqualTo,
    DataRequired,
    Optional,
    NumberRange,
    ValidationError,
)

from app import app
from app.models import (
    User,
    Time,
)

class Positive:
    def __init__(self):
        pass
    
    def __call__(self, form, field):
        if field.data is not None and field.data < 0:
            raise ValidationError('Number must be positive')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password')],
    )
    registration_key = StringField('Registration Key', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Please use a different email address')

    def validate_registration_key(self, registration_key):
        if registration_key.data != app.registration_key:
            raise ValidationError('Invalid registration key')

class EventForm(FlaskForm):
    suggested_times = StringField(
        "Or suggest a new time (as many as you'd like, seperated by commas)",
    )
    submit = SubmitField('Submit')

class NewEventForm(FlaskForm):
    description = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create Event')

class EditEventForm(FlaskForm):
    description = StringField('Edit Name', validators=[DataRequired()])
    submit = SubmitField('Submit Edits')
