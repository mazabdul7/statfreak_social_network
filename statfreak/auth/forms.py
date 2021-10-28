'''Code by Mazin Abdulmahmood, Ben Li'''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField, DecimalRangeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, Regexp
from statfreak.models import User, Area
from flask_wtf.file import FileField, FileAllowed
from statfreak import photos
from flask_login import current_user


class SignupForm(FlaskForm):
    first_name = StringField(label='First name', validators=[
                             DataRequired(), Length(min=3)], render_kw={"placeholder": "First Name"})
    last_name = StringField(label='Last name', validators=[
                            DataRequired(), Length(min=3)], render_kw={"placeholder": "Last Name"})
    email = EmailField(label='Email address', validators=[
                       DataRequired()], render_kw={"placeholder": "Email"})
    username = StringField(label="Username", validators=[DataRequired(), Length(
        min=3, max=12), Regexp(r'^[\w]+$')], render_kw={"placeholder": "Username"})
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=6)], render_kw={"placeholder": "Password"})
    password_repeat = PasswordField(label='Repeat Password', validators=[DataRequired(), Length(min=6), EqualTo(
        'password', message='Passwords must match!')], render_kw={"placeholder": "Repeat Password"})

    def validate_email(self, email):
        users = User.query.filter_by(email=email.data).first()

        if users is not None:
            raise ValidationError(
                'An account is already registered for that email address')

    def validate_username(self, username):
        users = User.query.filter_by(username=username.data).first()

        if users is not None:
            raise ValidationError(
                'An account is already registered with that username')


class LoginForm(FlaskForm):
    email = EmailField(label='Email address', validators=[
                       DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=6)], render_kw={"placeholder": "Password"})
    remember = BooleanField("Remember Me")

    def validate_email(self, email):
        users = User.query.filter_by(email=email.data).first()

        if users is None:
            raise ValidationError(
                'No account is registered with that email address')

    def validate_password(self, password):
        users = User.query.filter_by(email=self.email.data).first()

        if users is not None:
            if not users.check_password(password=password.data):
                raise ValidationError('Invalid password')


class ProfileForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(
        min=3, max=12)], render_kw={"placeholder": "Username"})
    bio = TextAreaField(label='Bio', render_kw={"placeholder": "Bio"})
    area = QuerySelectField(
        label='Your location', query_factory=lambda: Area.query.all(), get_label='area_name')
    photo = FileField('Profile picture', validators=[
                      FileAllowed(photos, 'Images only!')])
    university = SelectField(label='My university', choices=[
                             "Imperial College London", "Kings College London", "Queen Mary's University", "University College London"])
    roommates = SelectField(label='Number of roomates', choices=[(
        0, "Just me"), (1, "One friend"), (2, "Two friends"), (3, "Three friends"), (4, "Four friends")])
    min_price = DecimalRangeField(label="My minimum price", default=0)
    max_price = DecimalRangeField(label="My maximum price", default=0)

    def validate_username(self, username):
        users = User.query.filter_by(username=username.data).first()
        if users is not None and users.username != current_user.username:
            raise ValidationError(
                'An account is already registered with that username')


class BlogForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired(), Length(
        min=3, max=50)], render_kw={"placeholder": "Post title"})
    content = TextAreaField(label='Content', validators=[
                            DataRequired(), Length(min=50)], render_kw={"placeholder": "Content"})
    area = QuerySelectField(label='Tag an area to your post:',
                            query_factory=lambda: Area.query.all(), get_label='area_name')


class CommentForm(FlaskForm):
    content = TextAreaField(label='Content', validators=[DataRequired()], render_kw={
                            "placeholder": "Write a comment here"})
