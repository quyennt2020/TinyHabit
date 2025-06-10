from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class HabitForm(FlaskForm):
    anchor_moment = StringField(
        "Anchor Moment (e.g., 'After I brush my teeth')",
        validators=[DataRequired(), Length(max=255)]
    )
    tiny_behavior = StringField(
        "New Tiny Habit (e.g., 'I will floss one tooth')",
        validators=[DataRequired(), Length(max=255)]
    )
    celebration = StringField(
        "Celebration (e.g., 'I will say \"Good job!\"')",
        validators=[DataRequired(), Length(max=255)]
    )
    submit = SubmitField('Add Habit')
