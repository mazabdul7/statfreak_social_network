'''
Test forums functionality
Code by Mazin Abdulmahmood, Toby Katerbau
'''
from statfreak.models import Wellbeing, Profile

def test_create_entry(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to create a wellbeing entry
    WHEN When they successfully submit their quiz
    THEN they should see their new entry listed in the page
    """
    count1 = Wellbeing.query.count()

    profile = Profile.query.filter_by(user_id=user_with_profile.id).first()
    response = client.post('/wellbeing', data=dict(
        happy=8, satisfied=9, anxiety=2, notes='Sample notes', user_id=user_with_profile.id,
        location=profile.area
        ), follow_redirects=True)

    count2 = Wellbeing.query.count()

    assert count2-count1 == 1
    assert b'Sample notes' in response.data
    assert b'Entry successfully entered' in response.data

def test_entry_cooldown(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to create a wellbeing entry 
    WHEN When they have already created an entry
    THEN they should be displayed a message telling them
    they have already created a post. The create entry
    button should not be rendered
    """
    profile = Profile.query.filter_by(user_id=user_with_profile.id).first()
    response = client.post('/wellbeing', data=dict(
        happy=8, satisfied=9, anxiety=2, notes='Sample notes', user_id=user_with_profile.id,
        location=profile.area
        ), follow_redirects=True)

    assert b'Entry successfully entered' in response.data
    assert b'You have already made an entry today, please come back later' in response.data
    assert b'Create new entry' not in response.data
