from statfreak import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.Text, nullable=False)
    lastname = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    profiles = db.relationship('Profile', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"{self.id} {self.firstname} {self.lastname} {self.email} {self.password}"

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo = db.Column(db.Text)
    bio = db.Column(db.Text)
    area = db.Column(db.Text)
    university = db.Column(db.Text)
    roommates =  db.Column(db.Integer)
    min_price =  db.Column(db.Integer, nullable=False)
    max_price =  db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"{self.id} {self.user_id}"

#Intermediary table to map relations as a many-to-many relationship for the tags
area_blog = db.Table('area_blog',
    db.Column('area_name',db.Integer,db.ForeignKey('area.area_name'), primary_key=True),
    db.Column('blog_id', db.Integer,db.ForeignKey('blog.id'),primary_key=True)
)

tags_blog = db.Table('tags_blog',
    db.Column('name',db.Integer,db.ForeignKey('tag.name'), primary_key=True),
    db.Column('blog_id', db.Integer,db.ForeignKey('blog.id'),primary_key=True)
)

class Area(db.Model):
    area_name = db.Column(db.Text, primary_key=True, nullable=False)

    @property
    def serialize(self):
        return {
        'name': self.area_name    
        }

class Tag(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20))

    @property
    def serialize(self):
        return {
        'id': self.id,
        'name': self.name     
        }

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(50), nullable=False)
    content=db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags=db.relationship('Area',secondary=area_blog,backref=db.backref('blogs_associated',lazy="dynamic"))
 
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'views': self.views,
            'comment_count': self.comment_count,
            'user_id': self.user_id
        }

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content=db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

class Wellbeing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    happiness=db.Column(db.Integer, nullable=False)
    satisfaction=db.Column(db.Integer, nullable=False)
    anxiety=db.Column(db.Integer, nullable=False)
    notes=db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
