import os

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SECRET_KEY='dev'
    UPLOADED_PHOTOS_DEST = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static\img")

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testdb.db'
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False