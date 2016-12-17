# project/server/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'my_secret_key'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/travis_ci_test'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
    #     os.environ.get('DB_USER'),
    #     os.environ.get('DB_PASSWORD'),
    #     os.environ.get('DB_HOST'),
    #     os.environ.get('DB_NAME')
    # )


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/travis_ci_test'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
    #     os.environ.get('DB_USER'),
    #     os.environ.get('DB_PASSWORD'),
    #     os.environ.get('DB_HOST'),
    #     os.environ.get('DB_NAME')
    # )
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/travis_ci_test'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
    #     os.environ.get('DB_USER'),
    #     os.environ.get('DB_PASSWORD'),
    #     os.environ.get('DB_HOST'),
    #     os.environ.get('DB_NAME')
    # )
