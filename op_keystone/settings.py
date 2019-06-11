"""
Django settings for op_keystone project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from config import *
from corsheaders.defaults import default_headers


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lp-zkq_mnt27f4#i+ru6=5@h=sln9)8dqdi)v5+n+1_#*sz=^+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'corsheaders',
    'identity',
    'partition',
    'credence',
    'catalog',
    'assignment'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'op_keystone.middleware.AuthMiddleware',
]

ROOT_URLCONF = 'op_keystone.urls'

WSGI_APPLICATION = 'op_keystone.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = MYSQL_CONFIG

# Cache
CACHES = REDIS_CONFIG


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': (
                'email', 'phone', 'username', 'domain', 'name'
            ),
            'max_similarity': 0.7
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# CORS setting
CORS_ORIGIN_WHITELIST = (
    'localhost:8080',
    'op_web.ijunhai.com')
CORS_ALLOW_HEADERS = default_headers + (
    'X-Junhai-Token',
    'Access-Control-Allow-Origin'
)
CORS_ALLOW_CREDENTIALS = True


# token continuous valid time, unit minutes
ACCESS_TOKEN_VALID_TIME = 60
REFRESH_TOKEN_VALID_TIME = 2 * ACCESS_TOKEN_VALID_TIME


# auth route white list
ROUTE_WHITE_LIST = [
    ('/identity/login/', 'post'),
    ('/identity/refresh/', 'post'),
    ('/identity/captcha/', 'get'),
    ('/identity/phone-captcha/', 'post')
]

# auth policy white list
POLICY_WHITE_LIST = [
    ('/identity/logout/', 'post'),
    ('/identity/privilege-for-manage-actions/', 'get'),
    ('/identity/privilege-for-describe-actions/', 'get')
]