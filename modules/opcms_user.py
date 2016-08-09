"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from hashlib import md5

from bottle import request, route, view
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf, \
    require_logged_in
from models import User, Site


__author__ = 'João Neto'


@route('/user/admin', method='GET')
@route('/user/admin/', method='GET')
@view('user_admin.html')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_user')
@require_logged_in()
def user_admin_page(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Admin user url
    """

    # User logged in
    user = User.get(User.id == user_id_logged_in)

    # Call template
    return dict(site=site, host=host, user=user, csrf=csrf, logged_in=logged_in, user_id_logged_in=user_id_logged_in)


@route('/user/update/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_user', json_response=True)
@require_logged_in(json_response=True)
def user_update(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Admin user url
    """

    # POST parameters
    user_id = int(request.POST.getunicode('id'))
    email = request.POST.getunicode('email')
    password1 = request.POST.getunicode('password1')
    password2 = request.POST.getunicode('password2')
    name = request.POST.getunicode('name')

    # Verify user
    if user_id_logged_in != user_id:
        # Logout
        session = request.environ.get('beaker.session')
        session['logged_in'] = False
        session['user_id_logged_in'] = None

        # Return error
        return dict(status=False, info='Sem permissão para acessar')

    # Verify password
    if password1 != password2:
        return dict(status=False, info='Senhas não coincidem')

    # User logged in
    try:
        user = User.get(User.id == user_id_logged_in)
    except User.DoesNotExist:
        return dict(status=False, info='Usuário não encontrado')

    # Verify changed email
    if user.email != email:
        try:
            other_user = User.get(User.email == email)
            return dict(status=False, info='Email já registrado')
        except User.DoesNotExist:
            pass

    # Update user data
    try:
        user.email = email
        if len(password1) > 0:
            user.password = md5(password1.encode('utf-8')).hexdigest()
        user.name = name
        user.save()
    except IntegrityError as exp:
        # Return error
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Atualizado com sucesso')


@route('/user/recovery/<user_id:int>/<user_hash:re:[0-9a-f]+>/', method='GET')
@view('recovery.html')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_recovery')
def user_recovery_page(site, host, netloc, csrf, user_id, user_hash):
    """
    User recovery page url
    """

    # Logout
    session = request.environ.get('beaker.session')
    session['logged_in'] = False
    session['user_id_logged_in'] = None

    # User
    try:
        user = User.get(User.id == user_id, User.user_hash == user_hash)
    except User.DoesNotExist:
        return dict(site=site, host=host, csrf=csrf, recovery=False)

    # Site
    try:
        site = Site.get(Site.user == user)
    except Site.DoesNotExist:
        return dict(site=site, host=host, csrf=csrf, recovery=False)

    # Verify actived user and actived site
    if (not user.active) or (not site.active):
        return dict(site=site, host=host, csrf=csrf, recovery=False)

    # Login
    session['logged_in'] = True
    session['user_id_logged_in'] = user.get_id()

    # Return OK
    return dict(site=site, host=host, csrf=csrf, recovery=True, user=user)


@route('/user/recovery/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_recovery', json_response=True)
@require_logged_in(json_response=True)
def user_recovery(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    User recovery post url
    """

    # POST parameters
    user_id = int(request.POST.getunicode('id'))
    password1 = request.POST.getunicode('password1')
    password2 = request.POST.getunicode('password2')

    # Verify user
    if user_id_logged_in != user_id:
        # Logout
        session = request.environ.get('beaker.session')
        session['logged_in'] = False
        session['user_id_logged_in'] = None

        # Return error
        return dict(status=False, info='Sem permissão para acessar')

    # Verify password
    if password1 != password2:
        return dict(status=False, info='Senhas não coincidem')

    # User
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        return dict(status=False, info='Usuário não encontrado')

    # Site
    try:
        site = Site.get(Site.user == user)
    except Site.DoesNotExist:
        return dict(status=False, info='Site não encontrado')

    # Update user password
    try:
        if len(password1) > 0:
            user.password = md5(password1.encode('utf-8')).hexdigest()
        user.save()
    except IntegrityError as exp:
        # Return error
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Atualizado com sucesso')
