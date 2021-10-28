'''
Test various profile functionality of the user
Code by Mazin Abdulmahmood, Toby Katerbau
'''
from statfreak.models import Profile

def test_create_profile(client, user_no_profile):
    """
    GIVEN A user attempts to create a profile
    WHEN When they create the profile with no profile picture
    THEN they they should be redirected to their own profile page and
    should have a default avatar
    """
    count1 = Profile.query.filter_by(user_id=user_no_profile.id).count()

    client.post('/login', data=dict(
        email=user_no_profile.email,
        password='password1',
        remember=True
    ), follow_redirects=True)

    response = client.post('/create_profile', data=dict(
        username=user_no_profile.username, bio='Hello I am Person One and I am a bot.', area='Camden', university='University College London',
        roommates=3, my_range="100 ; 2000", photo=None
    ), follow_redirects=True)

    count2 = Profile.query.filter_by(user_id=user_no_profile.id).count()

    assert response.status_code == 200
    assert b'Your profile was successfully created' in response.data
    assert b'default.png' in response.data
    assert b'Person One' in response.data
    assert count2-count1 == 1


def test_create_profile_username_change_taken(client, user_no_profile):
    """
    GIVEN A user attempts to create a profile and changes their username
    WHEN When they create the profile by clicking the create profile button
    THEN they they should be warned that the username is already in use
    
    Note: Due to same use of algorithm for update profile, this test also
    covers changing to a taken username with the update profile function
    """
    client.post('/login', data=dict(
        email=user_no_profile.email,
        password='password1',
        remember=True
    ), follow_redirects=True)

    response = client.post('/create_profile', data=dict(
        username='mazabdul7', bio='Hello I am Person One and I am a bot.', area='Camden', university='University College London',
        roommates=3, my_range="100 ; 2000", photo=None
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'An account is already registered with that username' in response.data


def test_update_profile(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to edit their profile
    WHEN When they successfully edit properties such as their area or bio
    THEN they they should be redirected to their profile page with the new
    data displayed and the database should be updated successfully
    """
    profile_original = Profile.query.filter_by(
        user_id=user_with_profile.id).first()
    profile_original_bio = profile_original.bio
    profile_original_area = profile_original.area

    assert profile_original_bio == 'Hello'
    assert profile_original_area == 'Camden'

    response = client.post('/update_profile', data=dict(
        username=user_with_profile.username, bio='Changed', area='Hackney', university='University College London',
        roommates=3, my_range="100 ; 2000", photo=None
    ), follow_redirects=True)

    profile_new_bio = Profile.query.filter_by(
        user_id=user_with_profile.id).first().bio
    profile_new_area = Profile.query.filter_by(
        user_id=user_with_profile.id).first().area

    assert response.status_code == 200
    assert profile_new_bio == 'Changed'
    assert profile_new_area == 'Hackney'
    assert b'Hackney' in response.data


def test_display_profile(client, logged_in, user_with_profile):
    """
    GIVEN A user views a profile
    WHEN When they are redirected to the profile page
    THEN they they should see the user's profile card displayed with their full name
    and comments displayed at the bottom
    """
    response = client.get(
        '/display_profiles/'+str(user_with_profile.username), follow_redirects=True)

    assert response.status_code == 200
    assert b'Person One' in response.data
    assert b"Here are Person's latest posts" in response.data
