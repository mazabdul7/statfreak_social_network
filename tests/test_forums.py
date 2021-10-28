'''
Test forums functionality
Code by Mazin Abdulmahmood, Toby Katerbau
'''
from statfreak.models import Blog, Comments

def test_create_post(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to create a post
    WHEN When they successfully confirm the post
    THEN they should see their new post is displayed in the forums
    and their username is approprately linked to their post
    """
    count1 = Blog.query.count()

    response = client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    count2 = Blog.query.count()

    assert response.status_code == 200
    assert count2-count1 == 1
    assert b'Your post was successfully created' in response.data
    assert b'Hello I am Person One' in response.data
    assert b'PersonOne' in response.data
    assert b'Edit my post' in response.data


def test_create_and_view_post(client, logged_in, user_with_profile):
    """
    GIVEN A user successfully creates a post and wishes to view it
    WHEN When they click view post
    THEN they should see their new post is displayed and that
    the view count associated with the post increases
    """
    count1 = Blog.query.count()

    response = client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    count2 = Blog.query.count()

    assert response.status_code == 200
    assert count2-count1 == 1
    assert b'Your post was successfully created' in response.data
    assert b'Hello I am Person One' in response.data

    new_post = Blog.query.filter_by(user_id=user_with_profile.id).first()
    response = client.get('/blog/'+str(new_post.id), follow_redirects=True)
    view_count = Blog.query.filter_by(
        user_id=user_with_profile.id).first().views

    assert response.status_code == 200
    assert view_count == 1
    assert b'Hello I am Person One' in response.data
    assert b'PersonOne' in response.data
    assert b'Edit my post' in response.data


def test_search_borough(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to search 
    WHEN When they do enter a borough tag as a search term
    THEN all associated borough posts should be displayed
    """
    client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    response = client.post('/search/Camden', follow_redirects=True)

    assert response.status_code == 200
    assert b'You are viewing search results for: "Camden"' in response.data
    assert b'Hello I am Person One' in response.data


def test_search_normal(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to search 
    WHEN When they do enter a word as a search term
    THEN all associated posts that contain that term should be displayed
    """
    client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    response = client.post('/search/test content', follow_redirects=True)

    assert response.status_code == 200
    assert b'You are viewing search results for: "test content"' in response.data
    assert b'Hello I am Person One' in response.data


def test_search_no_result(client, logged_in, user_with_profile):
    """
    GIVEN A user attempts to search 
    WHEN When they do enter a word as a search term where there is no result
    THEN an error message should be displayed and they should be redirected 
    back to the forums
    """
    response = client.post('/search/test content', follow_redirects=True)

    assert response.status_code == 200
    assert b'No results match your search' in response.data
    assert b'All posts' in response.data


def test_add_comment(client, logged_in, user_with_profile):
    """
    GIVEN A user wants to write a comment under a post
    WHEN When they successfully post the comment
    THEN they should be redirected to the post and their comment
    should be visible and the comment counter should have increased.
    """
    count1 = Blog.query.count()

    response = client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    count2 = Blog.query.count()

    assert response.status_code == 200
    assert count2-count1 == 1

    post = Blog.query.filter_by(user_id=user_with_profile.id).first()
    response = client.post('/blog/'+str(post.id), data=dict(
        content='This is the test comment.',
        user_id=user_with_profile.id, blog_id=post.id
        ), follow_redirects=True)
    comment = Comments.query.filter_by(user_id=user_with_profile.id).first()

    assert response.status_code == 200
    assert b'Your comment was successfully posted' in response.data
    assert b'This is the test comment.' in response.data
    assert b'1 Comments' in response.data
    assert comment is not None
    assert comment.content == 'This is the test comment.'
    assert comment.user_id == user_with_profile.id


def test_delete_comment(client, logged_in, user_with_profile, db):
    """
    GIVEN A user attempts to remove their comment
    WHEN When they click the delete comment button
    THEN they should be alerted their comment is removed and
    their comment should be deleted
    """
    comment = Comments(content='This is the test comment.',
                       user_id=user_with_profile.id, blog_id=1)
    db.session.add(comment)
    db.session.commit()

    response = client.post(
        '/delete_comment/'+str(comment.id), follow_redirects=True)

    assert response.status_code == 200
    assert b'Comment successfully removed.' in response.data
    assert Comments.query.filter_by(blog_id=1).first() is None


def test_edit_post(client, logged_in, user_with_profile, db):
    """
    GIVEN A user attempts to edit their post
    WHEN When they fill the update form with valid information
    THEN they should be redirected to their post and it should
    have updated with the new content
    """
    client.post('/blog', data=dict(
        title='Hello I am Person One', content='This is the test content to be posted to the blog. This is the test content to be posted to the blog. Post Post Post.',
        user_id=user_with_profile.id, area='Camden'
        ), follow_redirects=True)

    post = Blog.query.filter_by(user_id=user_with_profile.id).first()
    response = client.get('/blog/'+str(post.id), follow_redirects=True)

    assert response.status_code == 200
    assert b'Hello I am Person One' in response.data

    response = client.post('/update_blog/'+str(post.id), data=dict(
        title='My new title', content='This is the updated content to be posted to the blog. This is the updated content to be posted to the blog. Up Up Up.'),
        follow_redirects=True)

    assert response.status_code == 200
    assert b'My new title' in response.data
    assert b'This is the updated content' in response.data
