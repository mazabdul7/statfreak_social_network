'''
Test user related functions and corner cases relating login and logout
Code by Mazin Abdulmahmood, Toby Katerbau
'''
from statfreak.models import User
import time

def test_profile_not_allowed_when_user_not_logged_in(client):
    """
    GIVEN A user is not logged
    WHEN When they access the profile menu option
    THEN they should be redirected to the login page
    """
    response = client.get('/my_profile', follow_redirects=True)

    assert response.status_code == 200
    assert b'Login' in response.data

def test_signup_succeeds(client):
    """
    GIVEN A user is not registered
    WHEN When they submit a valid registration form
    THEN they the should be redirected to the login with their name shown and there should be an additional
    record in the user table in the database
    """
    count = User.query.count()
    response = client.post('/signup', data=dict(
        first_name='Person',
        last_name='Two',
        email='person_2@people.com',
        username='PersonTwo',
        password='password2',
        password_repeat='password2'
        ), follow_redirects=True)
    count2 = User.query.count()
    assert count2 - count == 1
    assert response.status_code == 200
    assert b'Person Two' in response.data

def test_signup_taken_email(client):
    """
    GIVEN A user is not registered
    WHEN When they submit a valid registration form with a taken email
    THEN they the should be warned the email is already in use and redirected 
    back to the signup page to try again
    """
    count = User.query.count()

    client.post('/signup', data=dict(
        first_name='Person',
        last_name='Three',
        email='person_3@people.com',
        username='PersonThree',
        password='password2',
        password_repeat='password2'
        ), follow_redirects=True)

    count2 = User.query.count()

    response = client.post('/signup', data=dict(
        first_name='Person',
        last_name='Three',
        email='person_3@people.com',
        username='PersonFour',
        password='password2',
        password_repeat='password2'
        ), follow_redirects=True)

    count3 = User.query.count()

    assert count2 - count == 1
    assert response.status_code == 200
    assert count3 - count2 == 0
    assert b'An account is already registered for that email address' in response.data

def test_signup_taken_username_unmatched_passwords(client):
    """
    GIVEN A user is not registered
    WHEN When they submit a valid registration form with a taken username and mismatched passwords
    THEN they the should be warned the username is in use and that the passwords do not match
    then be redirected back to the signup page to try again
    """
    count = User.query.count()

    client.post('/signup', data=dict(
        first_name='Person',
        last_name='Four',
        email='person_4@people.com',
        username='PersonFour',
        password='password2',
        password_repeat='password2'
        ), follow_redirects=True)

    response = client.post('/signup', data=dict(
        first_name='Person',
        last_name='Five',
        email='person_5@people.com',
        username='PersonFour',
        password='password2',
        password_repeat='passwor'
        ), follow_redirects=True)

    count2 = User.query.count()

    assert count2 - count == 1
    assert response.status_code == 200
    assert b'An account is already registered with that username' in response.data
    assert b'Passwords must match' in response.data

def test_login_succeeds_and_existing_user(client, user_with_profile):
    """
    GIVEN A returning user attempts to log in
    WHEN When they submit a valid login form
    THEN they the should be redirected to the main page with their name shown in the
    header
    """
    response = client.post('/login', data=dict(
        email=user_with_profile.email,
        password='password1',
        remember=True
        ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Person' in response.data

def test_login_succeeds_and_new_user(client, user_no_profile):
    """
    GIVEN A brand new user logs in
    WHEN When they submit a valid login form and do not have a linked profile
    THEN they the should be redirected to the create profile page
    """
    response = client.post('/login', data=dict(
        email=user_no_profile.email,
        password='password1',
        remember=True
        ), follow_redirects=True)
    assert response.status_code == 200
    assert b'Create your profile' in response.data

def test_logout(client, logged_in):
    """
    GIVEN A logged in attempts to logout
    WHEN When they click the sign out link
    THEN they they should be redirected to the login page with a 
    success message indicating they have been logged out
    """
    response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b'You have been successfully signed out' in response.data