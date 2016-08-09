"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from bottle import request, route, redirect, view
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf, \
    require_logged_in, require_permissions
from models import Site


__author__ = 'João Neto'


@route('/admin', method='GET')
@route('/admin/', method='GET')
@require_site_registered()
def site_admin_page(site, host, netloc):
    """
    Admin redirect
    """

    # Verify site active
    if not site.active:
        redirect('/login/?redirect_url=%s' % request.url)

    redirect("/site/admin")


@route('/site/admin', method='GET')
@route('/site/admin/', method='GET')
@view('site_admin.html')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_site')
@require_logged_in()
def site_admin_page(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Admin site url
    """

    # Call template
    return dict(host=host, site=site, csrf=csrf, logged_in=logged_in, user_id_logged_in=user_id_logged_in)


@route('/site/update/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_site', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True, site_id_key='id')
def site_update(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Update site post url
    """

    # POST parameters
    site_id = int(request.POST.getunicode('id'))
    user_id = int(request.POST.getunicode('user'))
    site_email = request.POST.getunicode('site_email')
    site_owner = request.POST.getunicode('site_owner')
    site_template = request.POST.getunicode('site_template')
    site_title = request.POST.getunicode('site_title')
    site_description = request.POST.getunicode('site_description')
    site_copyright = request.POST.getunicode('site_copyright')
    page_title = request.POST.getunicode('page_title')
    page_content = request.POST.getunicode('page_content')
    address = request.POST.getunicode('address')
    map_url = request.POST.getunicode('map_url')
    phones = request.POST.getunicode('phones')
    whats_app_phones = request.POST.getunicode('whats_app_phones')
    facebook_url = request.POST.getunicode('facebook_url')
    twitter_url = request.POST.getunicode('twitter_url')

    # Update site data
    try:
        site.site_email = site_email
        site.site_owner = site_owner
        site.site_template = site_template
        site.site_title = site_title
        site.site_description = site_description
        site.site_copyright = site_copyright
        site.page_title = page_title
        site.page_content = page_content
        site.address = address
        site.map_url = map_url
        site.phones = phones
        site.whats_app_phones = whats_app_phones
        site.facebook_url = facebook_url
        site.twitter_url = twitter_url
        site.save()
    except IntegrityError as exp:
        # Return error
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Atualizado com sucesso')
