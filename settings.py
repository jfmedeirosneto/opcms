"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from email.utils import formataddr
import os

from bottle import TEMPLATE_PATH


__author__ = 'João Neto'


# Print all queries of peewee to stderr.
# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


# Main site settings
MAIN_EMAIL = 'admin@localhost.com'
MAIN_PASSWORD = '1234'
MAIN_NAME = 'John Smith'
DEFAULT_SENDER = formataddr((MAIN_NAME, MAIN_EMAIL), 'UTF-8')

# Path of installation of opcms
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Add template path for web server
VIEWS_DIR = 'views'
VIEWS_PATH = os.path.join(BASE_PATH, VIEWS_DIR)
TEMPLATE_PATH.insert(0, VIEWS_PATH)

# Static path
STATIC_DIR = 'static'
STATIC_URL = '/%s/<file_path:path>' % STATIC_DIR
STATIC_PATH = os.path.join(BASE_PATH, STATIC_DIR)

# Image path
IMAGE_DIR = 'img'
IMAGE_URL = '/%s/<file_path:path>' % IMAGE_DIR
IMAGE_PATH = os.path.join(BASE_PATH, IMAGE_DIR)

# Image size
ORIG_SIZE = (1440, 1440)
NORM_SIZE = (480, 480)
THUMB_SIZE = (240, 240)

# Modules path
MODULES_DIR = 'modules'
MODULES_PATH = os.path.join(BASE_PATH, MODULES_DIR)

# Templates path
TEMPLATES_DIR = 'templates'
TEMPLATES_URL = '/%s/<file_path:path>' % TEMPLATES_DIR
TEMPLATES_PATH = os.path.join(BASE_PATH, TEMPLATES_DIR)


# TODO: Error on set other language, the Cache-Control for static not work properly
# Language code for this installation
# try:
#     locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')
# except locale.Error:
#     try:
#         locale.setlocale(locale.LC_ALL, 'pt_BR')
#     except locale.Error:
#         locale.setlocale(locale.LC_ALL, '')


# SessionMiddleware opts
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.data_dir': './data/session',
    'session.auto': True
}