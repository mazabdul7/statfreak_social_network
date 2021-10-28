import pytest
from flask_testing import LiveServerTestCase

class TestingWellBeing(LiveServerTestCase):
    def test_navigate_to_wellbeing(self, chrome_driver, session, full_sign_in, create_post):
        '''
        GIVEN a user has logged in
        WHEN they click the wellbeing tab
        THEN they should be redirected to the correct page
        '''

        self.driver.get("http://127.0.0.1:5000/")
        #signing up and logging in
        full_sign_in

        # clicking wellbeing tab
        self.driver.find_element_by_link_text('My Wellbeing')

        #asserting correct navigation
        assert self.driver.title == 'Wellbeing'


    def creating_new_entry(self, app, chome_driver, session, full_sign_in, create_post):
        '''
        GIVEN a user has logged in and navigated to the wellbeing page
        WHEN a user clicks to create a new entry and creates a new entry
        THEN the entry should be saved in the database and a custom message displayed
        '''
        self.driver.get("http://127.0.0.1:5000/")
        #signing up and logging in
        full_sign_in()

        # clicking wellbeing tab
        self.driver.find_element_by_link_text('My Wellbeing')

        #creating post
        create_post()

        # finding unique message
        unique_text = self.driver.find_element_by_class('alert alert-success alert-dismissible fade show')
        assert unique_text == 'Entry successfully entered'
