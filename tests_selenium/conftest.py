import pytest
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from statfreak import create_app
from statfreak.configmodule import TestingConfig
from statfreak import db as _db
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains

@pytest.fixture(scope='session')
def app(request):
    app = create_app(TestingConfig)
    app.config['LIVESERVER_PORT'] = 0
    yield app


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
def user(db):
    """ Creates a user with a profile. """
    from statfreak.models import User, Profile
    user = User(firstname="Person", lastname='One', email='person1@people.com', username='PersonOne')
    user.set_password('password1')
    db.session.add(user)
    db.session.commit()

    profile = Profile(photo='default.png', bio='Hello', area='Camden', user_id=1, university='University College London', roommates=3, min_price=300, max_price=1500)
    db.session.add(profile)
    db.session.commit()
    return user

from selenium.webdriver import Chrome, ChromeOptions
import multiprocessing
webdriver = Chrome()


@pytest.fixture(scope='class')
def chrome_driver(request):
    """ Fixture for selenium webdriver with options to support running in GitHub actions"""
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    chrome_driver = webdriver(options=options)
    request.cls.driver = chrome_driver
    yield
    chrome_driver.close()


@pytest.fixture(scope='class')
def selenium(app):
    """
    Fixture to run the Flask app
    A better alternative would be to use flask-testing live_server
    """
    process = multiprocessing.Process(target=app.run, args=())
    process.start()
    yield process
    process.terminate()


@pytest.fixture(scope='function')
def signup():
    driver = chrome_driver

    # clicking signup button
    driver.find_element_by_link_text('Signup').click()
    driver.implicitly_wait(10)

    # entering details
    driver.find_element_by_id('first_name').send_keys('John')
    driver.find_element_by_id('last_name').send_keys('Smith')
    driver.find_element_by_id('email').send_keys('JohnSmith1@gmail.com')
    driver.find_element_by_id('username').send_keys('johnsmith1')
    driver.find_element_by_id('password').send_keys('johnsmith1')
    driver.find_element_by_id('password_repeat').send_keys('johnsmith1')

    # pressing signup
    driver.find_element_by_class_name('btn btn-primary btn-lg ripple-surface').click()

@pytest.fixture(scope='function')
def login():
    # entering elements
    driver = chrome_driver()
    driver.find_element_by_id('email').send_keys('johnsmith@gmail.com')
    driver.find_element_by_id('password').send_keys('johnsmith')

    #pressing login
    driver.find_element_by_class_name('btn btn-primary btn-lg ripple-surface').click()

@pytest.fixture(scope='function')
def create_profile():
    driver = chrome_driver()
    # typing profile details
    driver.find_element_by_id('username').sendkeys('johnsmith1')
    driver.find_element_by_id('bio').sendkeys('Hi my name is John')
    Select(driver.find_element_by_id('area')).select_by_visible_text('Camden')
    Select(driver.find_element_by_id('university')).select_by_visible_text('University College London')
    Select(driver.find_element_by_id('roommates')).select_by_visible_text('Just me')

    # pressing save
    driver.find_element_by_class_name('btn btn-primary btn-lg ripple-surface').click()

@pytest.fixture(scope='function')
def full_sign_in():
    # signing in
    signup()
    # logging in
    login()
    # creating profile
    create_profile()

@pytest.fixture(scope='function')
def create_post():
    driver = chrome_driver
    # pressing button
    driver.find_element_by_class_name('btn btn-primary btn-lg ripple-surface').click()
    slider = driver.find_element_by_name('happy')
    move = ActionChains(driver)
    move.click_and_hold(slider).move_by_offset(40, 0).release().perform()
    driver.find_element_by_xpath("//input[@type='submit']").click()

@pytest.fixture(scope='function')
def create_forum_post():
    driver = chrome_driver
    driver.find_element_by_xpath('/html/body/div[3]/nav/div/button').click()
    driver.find_element_by_name('title').send_keys('Test Post')
    driver.find_element_by_name('content').send_keys('Lorem ipsum dolor sit amet, consectetur adipiscing elit.')
    driver.find_element_by_css_selector('button.btn:nth-child(2)').click()
