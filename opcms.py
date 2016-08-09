"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import sys
from hashlib import md5

from bottle import route, static_file, view, template, default_app, run, request
from beaker.middleware import SessionMiddleware
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf
from models import User, Site, db
from settings import STATIC_URL, STATIC_PATH, IMAGE_DIR, IMAGE_URL, IMAGE_PATH, MODULES_PATH, TEMPLATES_PATH, \
    TEMPLATES_DIR, TEMPLATES_URL, session_opts, MAIN_EMAIL, MAIN_PASSWORD, MAIN_NAME
from utils import import_modules, import_templates, send_contact_email


__author__ = 'João Neto'


"""
Dinamic data
"""
modules_list = None
templates_dict = None

"""
Create Main Site Data
"""
MAIN_USER = None
MAIN_SITE = None
try:
    MAIN_USER = User.get(User.email == MAIN_EMAIL)
    MAIN_SITE = Site.get(Site.user == MAIN_USER)
except (User.DoesNotExist, Site.DoesNotExist) as e:
    with db.transaction():
        try:
            if not MAIN_USER:
                MAIN_USER = User.create(email=MAIN_EMAIL,
                                        password=md5(MAIN_PASSWORD.encode('utf-8')).hexdigest(),
                                        name=MAIN_NAME,
                                        active=True)
            if not MAIN_SITE:
                MAIN_SITE = Site.create(user=MAIN_USER,
                                        site_email=MAIN_EMAIL,
                                        active=True)
        except IntegrityError as ex:
            print("Main Data Fail:", ex)


# Verify Main Site Data
if (not MAIN_USER) or (not MAIN_SITE):
    print("Main User and Main Site not defined.")
    sys.exit(-1)


@route('/', method='GET')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_index')
def index_page(site, host, netloc, csrf):
    """
    Main page url
    """
    global templates_dict

    # Get template name from site
    template_name = site.site_template

    # Preview argument or template name from site
    template_name = request.GET.get('preview', template_name)

    # Images url
    img_url = '%s/%s/' % (host, IMAGE_DIR)

    # Default template
    tpl = template('index.html', site=site, host=host, csrf=csrf, img_url=img_url)

    # Load custom template
    if templates_dict:
        if template_name in templates_dict:
            tpl_module = templates_dict[template_name]
            tpl_url = '%s/%s/%s/' % (host, TEMPLATES_DIR, tpl_module.dir_name)
            original_tpl = '%s%s' % (tpl_url, tpl_module.original_file_name)
            tpl = template(tpl_module.file_path, site=site, host=host, csrf=csrf, img_url=img_url,
                           tpl_url=tpl_url, original_tpl=original_tpl, tpl_module=tpl_module)

    # Return template
    return tpl


@route('/contact/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_index', json_response=True)
def contact(site, host, netloc, csrf):
    """
    Contact form post url
    """

    # POST parameters
    site_id = int(request.POST.getunicode('site_id'))
    name = request.POST.getunicode('name')
    email = request.POST.getunicode('email')
    subject = request.POST.getunicode('subject')
    message = request.POST.getunicode('message')

    # Verify parameters
    if (site_id is None) or (name is None) or (email is None) or (subject is None) or (message is None):
        return dict(status=False, info='Falha envio da mensagem')

    # Verify site
    if site.id != site_id:
        return dict(status=False, info='Falha envio da mensagem')

    # Send email
    send_contact_email(host, name, email, site, subject, message)

    return dict(status=True, info='Obrigado! Mensagem enviada com sucesso')


@route(STATIC_URL)
@require_site_registered()
def server_static(site, host, netloc, file_path):
    """
    Serving static files
    """

    # Response static
    response_static = static_file(file_path, root=STATIC_PATH)

    # Non-cache static
    non_cache = []

    # Verify non_cache files
    if file_path in non_cache:
        response_static.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
        response_static.set_header("Pragma", "no-cache")
        response_static.set_header("Expires", "0")
    else:
        response_static.set_header("Cache-Control", "max-age=86400, public")

    # Return static files
    return response_static


@route(IMAGE_URL)
@require_site_registered()
@require_site_activated()
def server_static(site, host, netloc, file_path):
    """
    Serving image files
    Images files is served by site according get_image_path function
    """

    # Response static
    response_static = static_file(file_path, root=site.get_image_path(IMAGE_PATH))

    # Force Brownser check a fresh static "If-Modified-Since"
    # response_static.set_header("Cache-Control", "max-age=86400, must-revalidate")
    # response_static.set_header("Expires", "-1")

    # Non-cache for images
    response_static.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response_static.set_header("Pragma", "no-cache")
    response_static.set_header("Expires", "0")

    # Return files files
    return response_static


@route(TEMPLATES_URL)
@require_site_registered()
@require_site_activated()
def server_template(site, host, netloc, file_path):
    """
    Serving template files
    """

    # Response static
    response_static = static_file(file_path, root=TEMPLATES_PATH)

    # Cache all template files
    response_static.set_header("Cache-Control", "max-age=86400, public")

    # Return static files
    return response_static


def get_opcms_app(modules_path, templates_path):
    """
    Get the OpCMS bottle app
    """
    global modules_list, templates_dict

    # Import all modules from modules_path
    modules_list = import_modules(modules_path)

    # Import all modules from modules_path
    templates_dict = import_templates(templates_path)

    # SessionMiddleware
    session_app = SessionMiddleware(default_app(), session_opts)

    # Return app
    return session_app


def main():
    """
    Main routine
    """

    # Run server
    # reloader=True
    run(app=get_opcms_app(MODULES_PATH, TEMPLATES_PATH), host='0.0.0.0', port=80, debug=True)


if __name__ == '__main__':
    main()
