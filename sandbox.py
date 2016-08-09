"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from bottle import route, static_file, view, app, run
from beaker.middleware import SessionMiddleware

from decorators import require_site_registered
from settings import STATIC_URL, STATIC_PATH, IMAGE_URL, IMAGE_PATH, session_opts


__author__ = 'João Neto'

"""
########### SANDBOX START
"""







"""
########### SANDBOXEND
"""


@route('/', method='GET')
@view('sandbox.html')
@require_site_registered()
def index_page(site, host, netloc):
    """
    Main page url
    """

    return dict(site=site, host=host)


@route(STATIC_URL)
def server_static(file_path):
    """
    Serving static files
    """

    # Return static files
    return static_file(file_path, root=STATIC_PATH)


@route(IMAGE_URL)
@require_site_registered()
def server_static(site, host, netloc, file_path):
    """
    Serving image files
    """

    # Return files files
    return static_file(file_path, root=site.get_image_path(IMAGE_PATH))

# SessionMiddleware
app = SessionMiddleware(app(), session_opts)

# Run server
# reloader=True
run(app=app, host='0.0.0.0', port=80, debug=True)

