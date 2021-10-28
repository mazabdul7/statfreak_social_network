'''Code by Mazin Abdulmahmood'''
from flask import Blueprint, redirect, render_template, request, redirect, flash, url_for
from flask_login.utils import login_required
from flask_login import current_user
from statfreak.auth.forms import CommentForm, ProfileForm, BlogForm
from statfreak.models import Profile, User, Blog, Area, Comments
from statfreak import db, photos
from statfreak.main.views import profile_required
from sqlalchemy import or_
from django.db import IntegrityError

community_bp = Blueprint('community', __name__)


@community_bp.route('/blog', methods=['GET', 'POST'])
@login_required
@profile_required
def blog():
    '''Forums page. Allows users to post and search the forums. Database error handling applied.
        returns all posts in forums database
        returns search boolean indicating search state for jinja in html template'''
    form = BlogForm()
    blogs = Blog.query.all()
    data = []
    newline = False
    newline_count = 0

    for blog in blogs:
        profile = Profile.query.filter_by(user_id=blog.user_id).first()
        photo = photos.url(profile.photo)
        user = User.query.filter_by(id=blog.user_id).first()

        for tag in blog.tags:
            tags = tag.serialize

        newline_count += 1
        if newline_count % 4 == 0:
            newline = True
        else:
            newline = False

        data.append([blog.serialize, user, photo, tags, newline])

    if request.method == 'POST' and form.validate_on_submit():
        new_blog = Blog(title=form.title.data,
                        content=form.content.data, user_id=current_user.id)
        area_tag = Area.query.filter_by(
            area_name=form.area.data.area_name).first()
        # add area as a tag to post for filtering later through relational db
        area_tag.blogs_associated.append(new_blog)

        try:
            db.session.add(new_blog)
            db.session.commit()
            flash("Your post was successfully created", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An error occured when creating the post", 'error')
            return redirect(url_for('community.blog'))

        return redirect(url_for('community.blog'))

    return render_template('blog.html', posts=data, form=form, search=False)


@community_bp.route('/search/', methods=['GET', 'POST'])
@community_bp.route('/search/<term>', methods=['GET', 'POST'])
@login_required
@profile_required
def search(term=None):
    '''Search function for forum posts by title, content and tags. Error flash if 
        search term is empty or user visits route through unnoficial channels.
        returns all matching posts'''
    if request.method == 'POST' or term is not None:
        if request.form:
            term = request.form['search_term']

        if term == "":
            flash("Enter something to search for!", "danger")
            return redirect(url_for("community.blog"))

        blogs = Blog.query.filter(
            or_(Blog.title.contains(term), Blog.content.contains(term))).all()
        tagged_blogs = Blog.query.join(Area.blogs_associated).filter(Area.area_name.contains(
            term)).all()  # query area through many-to-many tag relational db

        blogs.extend(tagged_blogs)

        if not blogs:
            flash("No results match your search", "warning")
            return redirect(url_for("community.blog"))

        form = BlogForm()
        data = []

        for blog in blogs:
            profile = Profile.query.filter_by(user_id=blog.user_id).first()
            photo = photos.url(profile.photo)
            user = User.query.filter_by(id=blog.user_id).first()

            for tag in blog.tags:
                tags = tag.serialize
            # data holds [post, user account, photo, tags]
            data.append([blog.serialize, user, photo, tags])

        return render_template('blog.html', posts=data, form=form, search=True, term=term)

    flash("Enter something to search for!", "danger")
    return redirect(url_for("community.blog"))


@community_bp.route('/blog/<id>', methods=['GET', 'POST'])
@login_required
@profile_required
def get_single_blog(id):
    '''Retrieves single forum post and any comments associated with the post.
        returns post and user comments'''
    form = CommentForm()

    blog = Blog.query.filter_by(id=id).first()

    if blog is None:
        flash("That post does not exist.", "danger")
        return redirect(url_for('community.blog'))

    profile = Profile.query.filter_by(user_id=blog.user_id).first()
    photo = photos.url(profile.photo)
    user = User.query.filter_by(id=blog.user_id).first()
    comment_data = []
    comments = Comments.query.filter_by(
        blog_id=blog.id).order_by(Comments.created_at.asc()).all()

    for comment in comments:
        temp_user = User.query.filter_by(id=comment.user_id).first()
        temp_profile = Profile.query.filter_by(user_id=comment.user_id).first()
        comment_data.append(
            [comment, temp_user, photos.url(temp_profile.photo)])

    blog_data = blog.serialize
    blog_data["tags"] = []

    for tag in blog.tags:
        blog_data["tags"].append(tag.serialize)

    blog.views += 1
    db.session.commit()
    if request.method == 'POST' and form.validate_on_submit():
        comment = Comments(content=form.content.data,
                           user_id=current_user.id, blog_id=blog.id)
        blog.comment_count += 1

        try:
            db.session.add(comment)
            db.session.commit()
            flash("Your comment was successfully posted", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An error occured when posting the comment", 'error')

        return redirect(url_for('community.get_single_blog', id=blog.id))

    return render_template('view_post.html', data=blog_data, photo=photo, user=user, form=form, comments=comment_data)


@community_bp.route('/update_blog/<id>', methods=['GET', 'POST'])
@login_required
@profile_required
def update_blog(id):
    '''Update forum post. Error handling applied incase unidentified user tries to edit
        a post they did not create. Also db commit error is handled.'''
    post = Blog.query.filter_by(id=id).first()

    if current_user.id == post.user_id:
        form = BlogForm(obj=post)

        if request.method == 'POST' and form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            try:
                db.session.commit()
                flash("Your post was successfully updated", "success")
            except IntegrityError:
                db.session.rollback()
                flash("An error occured when updating the post", 'error')

            return redirect(url_for('community.get_single_blog', id=id))
        return render_template('update_blog.html', form=form)
    else:
        flash("Oops, thats not allowed", "danger")
        return redirect(url_for('community.blog'))


@community_bp.route('/delete_blog/<id>', methods=['GET', 'POST'])
@login_required
@profile_required
def delete_blog(id):
    '''Delete user posts. Error handling to keep user from deleting posts they did not create.
        Also deletes any comments associated with the blog post.'''
    post = Blog.query.filter_by(id=id).first()
    comments = Comments.query.filter_by(blog_id=post.id).all()

    if current_user.id == post.user_id:
        db.session.delete(post)
        if comments:
            for comment in comments:
                db.session.delete(comment)
        db.session.commit()
        flash("Post successfully removed.", "success")
    else:
        flash("Oops, thats not allowed", "danger")

    return redirect(url_for('community.blog'))


@community_bp.route('/delete_comment/<id>', methods=['GET', 'POST'])
@login_required
@profile_required
def delete_comment(id):
    '''Delete user comments. Error handling to keep user from deleting comments they did not create
        Subtract comment counter from blog post'''
    comment = Comments.query.filter_by(id=id).first()
    post = Blog.query.filter_by(id=comment.blog_id).first()

    if current_user.id == comment.user_id:
        if post:
            post.comment_count -= 1
        db.session.delete(comment)
        db.session.commit()
        flash("Comment successfully removed.", "success")
    else:
        flash("Oops, thats not allowed", "danger")

    return redirect(url_for('community.get_single_blog', id=comment.blog_id))


@community_bp.route('/my_profile', methods=['GET', 'POST'])
@login_required
@profile_required
def my_profile():
    '''View own profile. If no profile redirect to create profile page'''
    result = Profile.query.join(User).filter(
        Profile.user_id == current_user.id).first()

    if result is not None:
        return redirect(url_for('community.display_profiles', username=current_user.username))
    else:
        return redirect(url_for('community.create_profile'))


@community_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@profile_required
def edit_profile():
    '''Edit own profile'''
    result = Profile.query.join(User).filter(
        Profile.user_id == current_user.id).first()

    if result is not None:
        return redirect(url_for('community.update_profile'))
    else:
        return redirect(url_for('community.create_profile'))


@community_bp.route('/create_profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    '''Create user profile'''
    form = ProfileForm(username=current_user.username)
    user = User.query.filter_by(username=current_user.username).first()

    if request.method == 'POST' and form.validate_on_submit():
        filename = "default.png"
        if 'photo' in request.files:
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])

        pricing = request.form['my_range']
        min_price = int(pricing.split(";")[0])
        max_price = int(pricing.split(";")[1])

        p = Profile(area=form.area.data.area_name, photo=filename, bio=form.bio.data, university=form.university.data, roommates=form.roommates.data,
                    min_price=min_price, max_price=max_price, user_id=current_user.id)
        user.username = form.username.data

        try:
            db.session.add(p)
            db.session.commit()
            flash("Your profile was successfully created", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An error occured when creating your profile", 'error')
            return redirect(url_for('community.create_profile'))

        return redirect(url_for('community.display_profiles', username=form.username.data))

    return render_template('profile.html', form=form, create=True)


@community_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
@profile_required
def update_profile():
    '''Update own profile and user preferences'''
    profile = Profile.query.join(User).filter_by(id=current_user.id).first()

    form = ProfileForm(obj=profile, username=current_user.username)

    if request.method == 'POST' and form.validate_on_submit():
        if 'photo' in request.files:
            if request.files['photo'].filename != '':
                filename = photos.save(request.files['photo'])
                profile.photo = filename

        pricing = request.form['my_range']
        profile.min_price = int(pricing.split(";")[0])
        profile.max_price = int(pricing.split(";")[1])
        profile.area = form.area.data.area_name
        profile.bio = form.bio.data
        profile.university = form.university.data
        profile.roommates = form.roommates.data
        current_user.username = form.username.data

        try:
            db.session.commit()
            flash("Your profile was successfully updated", "success")
        except IntegrityError:
            db.session.rollback()
            flash("An error occured when updating your profile", 'error')

        return redirect(url_for('community.display_profiles', username=current_user.username))

    return render_template('profile.html', form=form)


@community_bp.route('/display_profiles/<username>', methods=['POST', 'GET'])
@login_required
@profile_required
def display_profiles(username):
    '''Display a profile for a passed username.'''
    users = User.query.filter_by(username=username).first()
    results = Profile.query.join(User).filter_by(username=username).first()
    posts = Blog.query.filter_by(user_id=users.id).all()

    if not results:
        return redirect(url_for("community.blog"))
    url = photos.url(results.photo)
    return render_template('display_profile.html', profiles=results, photourl=url, users=users, posts=posts)
