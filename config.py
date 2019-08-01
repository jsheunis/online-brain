import os

DEFAULT_HOST = '0.0.0.0'

DEFAULT_PORT = '8080'

# Statement for enabling the development environment
DEBUG = False

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADED = True

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2
