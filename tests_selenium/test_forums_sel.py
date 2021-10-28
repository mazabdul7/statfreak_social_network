import pytest
from flask_testing import LiveServerTestCase

class TestingForums(LiveServerTestCase):
    def test_navigate_to_forumn_page(self, app, chrome_driver, full_sign_in):
        '''
        GIVEN a user has logged in
        WHEN a user clicks the forums tab
        THEN they should be redirected to the correct page
        '''
        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click
        # asserting correct page
        assert self.driver.title == 'Forums'


    def test_creating_post(self, app, chrome_driver, full_sign_in, create_forum_post):
        '''
        GIVEN the user is on the forums page and has logged in
        WHEN the user attempts to create a post
        THEN they should be able to create a post and a new message appears
        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click
        # creating post
        create_forum_post()
        # asserting unique message appears

        assert self.driver.find_element_by_css_selector('.alert > span:nth-child(1)') == 'Your Post was created successfully'
        assert self.driver.find_element_by_css_selector('div.container-fluid:nth-child(3) > div:nth-child(1) > ul:nth-child(5) > li:nth-child(1)') != None


    def test_search(self, app, chrome_driver, session, full_sign_in, create_forum_post):
        '''
        GIVEN there are some posts and the user has logged in
        WHEN the user searches for a term
        THEN the page should give an output for the search term with custom message
        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click
        # creating post
        create_forum_post()
        # searching for post
        self.driver.find_element_by_class('form-control').send_keys('Test')
        assert self.driver.find_element_by_css_selector('h4.text-muted') == 'You are viewing results for: "test"'


    def test_like(self, chrome_driver, app, session, full_sign_in):
        '''
        GIVEN there is a post which has been created
        WHEN a user clicks like on a post
        THEN the post should increase in likes
        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click

        # finding like on existing post and clicking
        self.driver.find_element_by_css_selector('div.container-fluid:nth-child(2) > div:nth-child(1) > div:nth-child(3) > button:nth-child(1)').click()

        # query database to see if likes has increased
        assert False


    def test_comment(self, chrome_driver, session, full_sign_in):
        '''
        GIVEN there is a post which has been created
        WHEN a user adds a comment to the post
        THEN the post should have that comment added
        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click

        # comment button
        self.driver.find_element_by_css_selector('a.ripple-surface').click()
        self.driver.find_element_by_css_selector('self.driver.find_element_by_css_selector').send_keys('Testing out a comment')
        self.driver.find_element_by_css_selector('button.btn:nth-child(1)').click()

        # asserting custom message displayed
        assert self.driver.find_element_by_css_selector('.alert') == 'Your comment was successfully posted'
        # asserting number of comments has increased
        assert self.driver.find_element_by_css_selector('.row:nth-child(3) > div:nth-child(1) > p:nth-child(2) > a:nth-child(5)') == '2 Comments'


    def test_view_post(self, chrome_driver, app, session, full_sign_in, create_forum_post):
        '''
        GIVEN there is a post and the user has logged in
        WHEN a user presses to view post
        THEN the user should be able to see the post clearly
        '''

        self.driver.get("http://127.0.0.1:5000/")

        # signing in
        full_sign_in()
        # clicking forums button
        self.driver.find_element_by_link_text('Forums').click
        # creating post
        create_forum_post()

        # clicking on post
        self.driver.find_element_by_link_text('View post').click()

        # asserting correct post was navigated to
        assert self.driver.find_element_by_css_selector('div.container-fluid-md:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > p:nth-child(1)') == 'Testing posting across multiple accounts! WOW this app is wavy. Could do with a rating system on posts and comments :) implement these!'




