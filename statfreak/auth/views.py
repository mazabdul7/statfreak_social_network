'''Code by Mazin Abdulmahmood'''
from flask import render_template, request, redirect, flash, url_for, abort
from flask import Blueprint
from statfreak.auth.forms import SignupForm, LoginForm
from statfreak import db, login_manager
from statfreak.models import User
from django.db import IntegrityError
from urllib.parse import urlparse, urljoin
from datetime import timedelta
from flask_login import login_user, logout_user, current_user
from flask_login.utils import login_required


auth_bp = Blueprint('auth', __name__)


def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in ('http', 'https') and host_url.netloc == redirect_url.netloc


def get_safe_redirect():
    url = request.args.get('next')
    if url and is_safe_url(url):
        return url
    url = request.referrer
    if url and is_safe_url(url):
        return url
    return '/'


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    '''Sign up page. Error handling incase db error occur'''
    form = SignupForm()

    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        user = User(firstname=form.first_name.data, lastname=form.last_name.data,
                    email=form.email.data, username=form.username.data)
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(
                f"Hello, {user.firstname} {user.lastname}. You are signed up.")
        except IntegrityError:
            db.session.rollback()
            flash(f'Error, unable to register {form.email.data}. ', 'error')
            return redirect(url_for('auth.signup'))

        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''Login page. Safe redirect to avoid malicous site redirects.'''
    form = LoginForm()

    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, remember=form.remember.data,
                   duration=timedelta(minutes=5))
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('main.index', name=user.firstname))

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been successfully signed out")
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    """ Takes a user ID and returns a user object or None if the user does not exist"""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))
