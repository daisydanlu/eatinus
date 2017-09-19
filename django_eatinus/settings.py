

import os.path
import django.contrib.auth

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('pmrayrayray', 'pmrayrayray@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'd6rm1ignhb18hl',  # Or path to database file if using sqlite3.
        'USER': 'ubrngrdjoltkvj',  # Not used with sqlite3.
        'PASSWORD': 'SEdCQXR4Y7Nhuiak1ZmQHm6BZX',  # Not used with sqlite3.
        'HOST': 'ec2-54-204-17-24.compute-1.amazonaws.com',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.
    }
}
# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'deploy/static')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2eatw#dqh#d@z2$w)&uvtgnk_w%h0co3)6$-(rfsrt11wor+xxj'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
  os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'eatinus',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles', 
    'django.contrib.admin',
    'django.contrib.localflavor',
    "gunicorn",
    'storages',
    'crispy_forms',
    'gravatar'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.static',      
    'django.core.context_processors.media',                     
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

django.contrib.auth.LOGIN_URL = '/login/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

#Amazon S3 settings
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')

AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = 'eatinus'
AWS_MEDIA_BUCKET_NAME = 'eatinus_media'

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

S3_STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
S3_MEDIA_URL = 'http://' + AWS_MEDIA_BUCKET_NAME + '.s3.amazonaws.com/'

STATIC_URL = S3_STATIC_URL

MEDIA_URL = S3_MEDIA_URL


# Heroku config
# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

