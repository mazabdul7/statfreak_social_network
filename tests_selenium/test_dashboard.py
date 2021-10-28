import pytest
import selenium
from flask_testing import LiveServerTestCase


class TestDashboard(LiveServerTestCase):

    def test_navigation_to_dashboard(self, app, signup, login, create_profile):
        '''
        GIVEN the user is a new user
        WHEN they sign up and login
        THEN they should be able to navigate to the dashboard

        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing up
        signup()
        assert self.driver.title() == 'signup'
        # logging in
        login()
        assert self.driver.title() == 'create_profile'
        # creating profile
        create_profile()
        assert self.driver.title() == 'Profiles'

        # going to homepage with dashboard
        self.driver.find_element_by_link_text('Home').click()
        assert self.driver.title() == 'Home'

    def test_quartile_statistics_graph(self, full_sign_in):
        '''
        GIVEN user has navigated to home page
        WHEN the user changes values in drop down menus
        THEN the graph should update appropriately
        '''

        self.driver.get("http://127.0.0.1:5000/")

        full_sign_in()
        assert False

    def test_average_price_per_person_room_size_graph(self):
        '''
        GIVEN a user has navigated to home page
        WHEN the user changes values in the dropdown menu
        THEN the appropriate graph should update
        '''
        assert False

    def test_average_crime_graph(self):
        '''
        GIVEN a user has navigate to crime and national statistics tab on the home page
        WHEN the user adds or removes crimes from the dropdown menu
        THEN the graph should update appropriately
        '''
        assert False

    def test_comparison_well_being_statistics(self):
        '''
        GIVEN a user has navigate to crime and national statistics tab on the home page
        WHEN the user changes the values in the dropdown menu
        THEN the graph should update appropriately
        '''
        assert False

    def test_community_borough_leaderboard(self):
        '''
        GIVEN a user has navigated to the home page
        WHEN the user selects the community borough leaderboard
        THEN the page should navigate to the correct tab and display the correct graphic
        '''
        assert False
