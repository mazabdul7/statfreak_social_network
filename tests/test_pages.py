'''
Test that superficially accessible pages of the site load properly
Code by Mazin Abdulmahmood, Toby Katerbau
'''

def test_forums(client, logged_in):
    """
    GIVEN A logged in user accesses the forums
    WHEN When they click the page link in the navbar
    THEN they they should be redirected to the page
    """
    response = client.get('/blog', follow_redirects=True)

    assert response.status_code == 200
    assert b'Forums' in response.data

def test_wellbeing_quiz(client, logged_in):
    """
    GIVEN A logged in user accesses the wellbeing section
    WHEN When they click the page link in the navbar
    THEN they they should be redirected to the page
    """
    response = client.get('/wellbeing', follow_redirects=True)

    assert response.status_code == 200
    assert b'My wellbeing' in response.data

def test_my_profile(client, logged_in):
    """
    GIVEN A logged in user accesses their profile
    WHEN When they click the page link in the navbar
    THEN they they should be redirected to the page
    """
    response = client.get('/my_profile', follow_redirects=True)

    assert response.status_code == 200
    assert b'Profile' in response.data

def test_home(client):
    """
    GIVEN A visitor opens the site
    WHEN When they load the site
    THEN they they should see the home page
    """
    response = client.get('/', follow_redirects=True)

    assert response.status_code == 200
    assert b'Home' in response.data

def test_edit_profile(client, logged_in):
    """
    GIVEN A logged in user with a profile tries edits their profile
    WHEN When they click the edit profile button
    THEN they they should be redirected to the edit profile page
    """
    response = client.get('/edit_profile', follow_redirects=True)

    assert response.status_code == 200
    assert b'Edit your profile' in response.data


def test_edit_profile_no_profile(client, user_no_profile):
    """
    GIVEN A logged in user without a profile tries edits their profile
    WHEN When they type the edit profile url manually
    THEN they should be redirected to the create profile page
    """
    client.post('/login', data=dict(
        email=user_no_profile.email,
        password='password1',
        remember=True
        ), follow_redirects=True)

    response = client.get('/edit_profile', follow_redirects=True)

    assert response.status_code == 200
    assert b'Create your profile' in response.data

def test_search_page(client, logged_in):
    """
    GIVEN A logged in user with a profile tries use the search route
    WHEN When they enter the search route without any search data
    THEN they should see a message telling them to enter a search term
    """
    response = client.get('/search', follow_redirects=True)

    assert response.status_code == 200
    assert b'Enter something to search for!' in response.data
