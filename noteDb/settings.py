"""
Django settings for noteDb project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os
import logging

# LDAP AUTH
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# read local settings file
from .local_settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'inLocalSettings'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'note',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # CORS
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
]

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CORS_ALLOW_CREDENTIALS = True


ROOT_URLCONF = 'noteDb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'noteDb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


##  ____  _____ ____ _____ 
## |  _ \| ____/ ___|_   _|
## | |_) |  _| \___ \ | |  
## |  _ <| |___ ___) || |  
## |_| \_\_____|____/ |_|  
##                         
REST_FRAMEWORK = {
    
    'DEFAULT_PERMISSION_CLASSES': (
        # if you comment this line, you can access the api without authentication
        'rest_framework.permissions.IsAuthenticated',


        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # 'rest_framework.permissions.AllowAny',
    ),

    ## JWT
    # Basic Auth    -   a username and password are passed with each API request. 
    #                   This provides only a minimum level of security and user credentials are visible in the URLs
    # Session Auth  -   requires the user to log in through the server-side application before using the API. 
    #                   This is more secure than Basic Auth but is not convenient for working with single-page apps in a framework like Angular.
    # JSON Web Tokens - are an industry standard mechanism for generating a token which can be passed in the HTTP headers of each request, 
    #                   authenticating the user. This is the mechanism we will use for authentication.

    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
    ),

}


##
##      ____.__      _____________
##     |    /  \    /  \__    ___/
##     |    \   \/\/   / |    |   
## /\__|    |\        /  |    |   
## \________| \__/\  /   |____|   
##                 \/             
##

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}



##   _     ____    _    ____  
##  | |   |  _ \  / \  |  _ \ 
##  | |   | | | |/ _ \ | |_) |
##  | |___| |_| / ___ \|  __/ 
##  |_____|____/_/   \_\_|    
##                           

# these are overridden by the local_settings.py file
#AUTH_LDAP_SERVER_URI = "ldap://ldap.OVERRIDDEN.local:389"
#AUTH_LDAP_BIND_DN = "cn=ldapsearchOVERRIDDENuser,cn=Users,dc=ldap,dc=local"
#AUTH_LDAP_BIND_PASSWORD = "passwordOVERRIDDEN"
#AUTH_LDAP_USER_SEARCH = LDAPSearch("cn=Users,dc=OVERRIDDEN,dc=local", ldap.SCOPE_SUBTREE, "(sAMAccountName=%(user)s)")

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# User authentication methods
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django_auth_ldap": {"level": "DEBUG", "handlers": ["console"]}},
}


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_ROOT = "static/"
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# folder containing files
FILES_DIRECTORY = 'files'


DATE_FORMAT_DB= "%Y-%m-%dT%H:%M:%S+0000"
DATE_FORMAT_LOG= "%Y%m%dT%H%M%SZ"

# log setup
# level: DEBUG, INFO, WARNING, ERROR, CRITICAL
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', 
                    datefmt='%Y%m%dT%H%M%SZ', 
                    filename='note.log', encoding='utf-8', level=logging.DEBUG)


HARD_CODED_ADMINS = ['moro', 'mcarraro']
