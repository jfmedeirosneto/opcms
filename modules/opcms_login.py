from hashlib import md5

from bottle import request, route, view
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf
from models import User, Site, db
from settings import DEFAULT_SENDER
from utils import send_recovery_email


__author__ = 'João Neto'


@route('/login', method='GET')
@route('/login/', method='GET')
@view('login.html')
@require_site_registered()
@require_csrf(token_id='csrf_login')
def login_page(site, host, netloc, csrf):
    """
    Login page url
    """

    # Logout
    session = request.environ.get('beaker.session')
    session['logged_in'] = False
    session['user_id_logged_in'] = None

    # Call template
    redirect_url = request.GET.get('redirect_url')
    return dict(site=site, host=host, csrf=csrf, redirect_url=redirect_url)


@route('/login/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_login', json_response=True)
def login(site, host, netloc, csrf):
    """
    Login post url
    """

    # Logout
    session = request.environ.get('beaker.session')
    session['logged_in'] = False
    session['user_id_logged_in'] = None

    # POST parameters
    redirect_url = request.POST.getunicode('redirect_url')
    email = request.POST.getunicode('email')
    password = request.POST.getunicode('password')

    # User
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        return dict(status=False, info='Usuário não encontrado')

    # Verify user
    if site.user != user:
        # Return error
        return dict(status=False, info='Sem permissão para acessar')

    # Verify user
    if not user.active:
        # Return error
        return dict(status=False, info='Usuário inativo')

    # Verify password
    if user.password != md5(password.encode('utf-8')).hexdigest():
        # Return error
        return dict(status=False, info='Senha incorreta')

    # Login
    session['logged_in'] = True
    session['user_id_logged_in'] = user.get_id()

    # Return OK
    return dict(status=True, info='Entrou com sucesso', redirect_url=redirect_url)


@route('/login/recovery/', method='POST')
@require_site_registered(json_response=True)
@require_csrf(token_id='csrf_login', json_response=True)
def login_recovery(site, host, netloc, csrf):
    """
    Recovery post url
    """

    # Logout
    session = request.environ.get('beaker.session')
    session['logged_in'] = False
    session['user_id_logged_in'] = None

    # POST parameters
    email = request.POST.getunicode('email')

    # User
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        return dict(status=False, info='Usuário não encontrado')

    # Site
    try:
        site = Site.get(Site.user == user)
    except Site.DoesNotExist:
        return dict(status=False, info='Site não encontrado')

    # Send recovery email
    send_recovery_email(host, DEFAULT_SENDER, user)

    # Return OK
    return dict(status=True, info='Solicitado senha com sucesso. Acesse seu email para recuperar sua senha.')


@route('/logout/', method=['GET', 'POST'])
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
def logout(site, host, netloc):
    """
    Logout url
    """

    # Logout
    session = request.environ.get('beaker.session')
    session['logged_in'] = False
    session['user_id_logged_in'] = None

    # Return OK
    return dict(status=True, info='Saiu com sucesso')
