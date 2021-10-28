'''Code by Mazin Abdulmahmood, Toby Katerbau'''
import pytest
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from statfreak import create_app
from statfreak.configmodule import TestingConfig
from statfreak import db as _db

@pytest.fixture(scope='session')
def app(request):
    """ Returns a session wide Flask app """
    _app = create_app(TestingConfig)
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()

@pytest.fixture(scope='session')
def client(app):
    """ Exposes the Werkzeug test client for use in the tests. """
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """
    Returns a session wide database using a Flask-SQLAlchemy database connection.
    """
    _db.app = app
    _db.create_all()

    yield _db

@pytest.fixture(scope='function', autouse=True)
def session(db):
    """ Rolls back database changes at the end of each test """
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)
    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()

@pytest.fixture(scope='function')
def user_no_profile(db):
    """ Creates a user with no profile. """
    from statfreak.models import User, Profile
    user = User(firstname="Person", lastname='One', email='person1@people.com', username='PersonOne')
    user.set_password('password1')
    db.session.add(user)
    db.session.commit()
    
    return user

@pytest.fixture(scope='function')
def user_with_profile(db):
    """ Creates a user with a profile. """
    from statfreak.models import User, Profile
    user = User(firstname="Person", lastname='One', email='person1@people.com', username='PersonOne')
    user.set_password('password1')
    db.session.add(user)
    db.session.commit()

    profile = Profile(photo='default.png', bio='Hello', area='Camden', user_id=user.id, university='University College London', roommates=3, min_price=300, max_price=1500)
    db.session.add(profile)
    db.session.commit()

    user = User.query.filter_by(username=user.username).first()
    return user

@pytest.fixture(scope='function')
def logged_in(client, user_with_profile):
    """ Logs into the main site for tests to access site functionality. """
    return client.post('/login', data=dict(
    email=user_with_profile.email,
    password='password1',
    remember=True
    ), follow_redirects=True)
