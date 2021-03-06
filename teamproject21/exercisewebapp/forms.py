from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from exercisewebapp.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class GroupCreateForm(FlaskForm):
    exercise_name = StringField('Exercise name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    #goal description etc -- can be changed to be more specific
    description = TextAreaField('Description', validators=[DataRequired(),Length(min=10, max=250)])
    submit = SubmitField('Create Group')


class PostForm(FlaskForm):
    title = StringField('Post title',
                                validators=[DataRequired(), Length(min=2, max=20)])
    content = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=250)])
    reps = IntegerField('Number of reps', validators=[DataRequired()])
    video = FileField('Video (.mp4)', validators=[FileRequired(), FileAllowed(['mp4'], 'Wrong format, you can only upload .mp4 files!')])
    group_id = IntegerField('Group id', validators=[DataRequired()])
    submit = SubmitField('Make Post')

class VoteForm(FlaskForm):
    upvote = SubmitField('Upvote')
    downvote = SubmitField('Downvote')
    myhiddenid = HiddenField()
