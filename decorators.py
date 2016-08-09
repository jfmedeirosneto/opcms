"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from _sha256 import sha256
import functools
import os

from bottle import request, abort, redirect

from models import Site


__author__ = 'João Neto'


def require_site_registered(json_response=False):
    """
    require_site_registered decorator
    Inject host and site variables args in function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Request host
            scheme = request.urlparts.scheme
            netloc = request.urlparts.netloc

            # Normalized host
            host = '%s://%s' % (scheme, netloc)
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            normalized_host = 'http://%s' % netloc

            # Get site information
            try:
                site = Site.get(Site.id == 1)
            except Site.DoesNotExist:
                msg = 'Site %s não existe neste servidor' % host
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(404, msg)

            # callback function with site and host arguments injected
            kwargs.update({'site': site, 'host': host, 'netloc': netloc})
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_site_activated(json_response=False):
    """
    require_site_activated decorator
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            site = kwargs.get('site')
            if not site.active:
                msg = 'Site inativo'
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(403, msg)

            # callback function
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_csrf(token_id='csrf', json_response=False):
    """
    require_csrf decorator
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session = request.environ.get('beaker.session')
            if request.method == 'POST':
                csrf = request.POST.get('csrf')
                if not csrf or csrf != session.get(token_id):
                    msg = 'Dados inválidos ou expirados, recaregue a página.'
                    if json_response:
                        return dict(status=False, info=msg)
                    else:
                        abort(403, msg)
            elif request.method == 'GET':
                csrf = sha256(os.urandom(8)).hexdigest()
                session[token_id] = csrf
            else:
                csrf = None
            # callback function with csrf argument injected
            kwargs.update({'csrf': csrf})
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_logged_in(json_response=False):
    """
    require_login decorator
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session = request.environ.get('beaker.session')
            logged_in = session.get('logged_in')
            user_id_logged_in = session.get('user_id_logged_in')
            if (not logged_in) or (not user_id_logged_in):
                if json_response:
                    return dict(status=False, info='Acesso necessita de login, recaregue a página.')
                else:
                    redirect('/login/?redirect_url=%s' % request.url)
            else:
                site = kwargs.get('site')
                if site.user.get_id() != user_id_logged_in:
                    session['logged_in'] = False
                    session['user_id_logged_in'] = None
                    msg = 'Sem permissão para acessar'
                    if json_response:
                        return dict(status=False, info=msg)
                    else:
                        abort(403, msg)
                elif not site.active:
                    session['logged_in'] = False
                    session['user_id_logged_in'] = None
                    msg = 'Site inativo'
                    if json_response:
                        return dict(status=False, info=msg)
                    else:
                        abort(403, msg)
                elif not site.user.active:
                    session['logged_in'] = False
                    session['user_id_logged_in'] = None
                    msg = 'Usuário inativo'
                    if json_response:
                        return dict(status=False, info=msg)
                    else:
                        abort(403, msg)

            # callback function with logged_in argument injected
            kwargs.update({'logged_in': logged_in, 'user_id_logged_in': user_id_logged_in})
            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(json_response=False, site_id_key='site', user_id_key='user'):
    """
    require_permissions decorator
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = 'Sem permissão para acessar'

            # Site data
            site = kwargs.get('site')

            # Session data
            session = request.environ.get('beaker.session')
            user_id_logged_in = session.get('user_id_logged_in')

            # Initialization
            site_id = -1
            user_id = -1

            # Verify request
            if request.method == 'POST':
                # POST parameters
                site_id = int(request.POST.get(site_id_key))
                user_id = int(request.POST.get(user_id_key))
            elif request.method == 'GET':
                site_id = int(kwargs.get('site_id'))
                user_id = int(kwargs.get('user_id'))
            else:
                # Abort
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(403, msg)

            # Verify permissions
            if user_id_logged_in != user_id:
                # Logout
                session['logged_in'] = False
                session['user_id_logged_in'] = None

                # Abort
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(403, msg)
            elif (not site_id) or (not user_id):
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(403, msg)
            elif (site.get_id() != site_id) or (site.user.get_id() != user_id):
                if json_response:
                    return dict(status=False, info=msg)
                else:
                    abort(403, msg)

            # callback function
            return func(*args, **kwargs)

        return wrapper

    return decorator