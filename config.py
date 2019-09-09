import os

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '8080'


class ConfigBase(object):

    DEBUG = False
    TESTING = False

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    THREADED = True

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(ConfigBase):
    # Define the SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + \
                              os.path.join(ConfigBase.BASE_DIR, 'app.db')


class DevelopmentConfig(ConfigBase):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + \
                              os.path.join(ConfigBase.BASE_DIR, 'app-dev.db')


class TestingConfig(ConfigBase):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + \
                              os.path.join(ConfigBase.BASE_DIR, 'app-test.db')


