import urllib.request
from flask_testing import LiveServerTestCase
import pytest
from statfreak.models import User
from selenium import webdriver
from statfreak.models import Profile


class TestMyAppBrowser(LiveServerTestCase):
    def test_app_is_running(self, app):
        '''
        GIVEN the testing has been initialised
        WHEN the app launches
        THEN it should have a correct response code to test if it is working
        '''
        self.driver.get("http://127.0.0.1:5000/")
        response = urllib.request.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_signup(self, app, signup, db, session):
        '''
        GIVEN a user has not been registered
        WHEN a user enters signup details
        THEN the user should be logged into the database
        '''
        self.driver.get("http://127.0.0.1:5000/")
        count = User.query.count()
        signup()

        # find new entry in sql database
        count2 = User.query.count()
        assert count2 == count + 1

    def test_login(self, app, signup, db, login, session):
        '''
        GIVEN a user has already signed up
        WHEN a user enters their login details
        THEN they should be logged in and directed to create a profile
        '''
        self.driver.get("http://127.0.0.1:5000/")

        # signing up
        signup()

        #logging in
        login()

        #assert correctly placed to create profile
        assert self.driver.title == 'create_profile'

    def test_create_profile(self, app, signup, login, create_profile, session):
        '''
        GIVEN a user has logged in
        WHEN the user enters their profile details and saves
        THEN they should be saved into the database
        '''
        self.driver.get("http://127.0.0.1:5000/")
        # signing up
        signup()

        # logging in
        login()

        # creating profile
        create_profile()

        # asserting title is correct
        assert self.driver.title == 'Profiles'

        # need to add stuff to query database and see if entered items are correct
        user = User.query.filter_by(username='johnsmith1')
        profile_new_bio = Profile.query.filter_by(
            user_id=user.id).first().bio

        assert user.bio == 'Hi my name is John'
