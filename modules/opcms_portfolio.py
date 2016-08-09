import os

from bottle import request, route, view, template
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf, \
    require_logged_in, require_permissions
from models import Portfolio, db
from settings import IMAGE_DIR, IMAGE_PATH, ORIG_SIZE, NORM_SIZE, THUMB_SIZE
from utils import upload_new_image, upload_image


__author__ = 'João Neto'


@route('/portfolios/admin', method='GET')
@route('/portfolios/admin/', method='GET')
@view('portfolios_admin.html')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_portfolios')
@require_logged_in()
def portfolios_admin_page(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Admin portfolios url
    """

    # Images url
    img_url = '%s/%s/' % (host, IMAGE_DIR)

    # Call template
    return dict(host=host, site=site, csrf=csrf, logged_in=logged_in, user_id_logged_in=user_id_logged_in,
                img_url=img_url)


@route('/portfolio/get/<site_id:int>/<user_id:int>/<portfolio_id:int>/', method='GET')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_permissions(json_response=True)
def portfolio_get(site, host, netloc, site_id, user_id, portfolio_id):
    """
    Get portfolio url
    """

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Images data
    site_img_url = '%s/%s/' % (host, IMAGE_DIR)
    original_url = site_img_url + portfolio.original_image
    normalized_url = site_img_url + portfolio.normalized_image
    thumbnail_url = site_img_url + portfolio.thumbnail_image

    # Return OK
    return dict(status=True,
                info='Portfólio encontrado com sucesso',
                original=original_url,
                normalized=normalized_url,
                thumbnail=thumbnail_url,
                **portfolio.get_dictionary())


@route('/portfolio/add/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_portfolios', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def portfolio_add(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Add portfolio post url
    """

    # POST parameters
    site_id = int(request.POST.get('site'))
    user_id = int(request.POST.get('user'))
    title = request.POST.get('title')
    description = request.POST.get('description')

    # Upload portfolio image
    start_index = 1
    try:
        portfolios = site.portfolios.order_by(Portfolio.id.desc())
        last_portfolio = portfolios.get()
        start_index = last_portfolio.id + 1
    except Portfolio.DoesNotExist:
        pass
    img_path = site.get_image_path(IMAGE_PATH)
    img_url = '%s/%s/' % (host, IMAGE_DIR)
    upload_response = upload_new_image(request, 'portfolio', start_index, img_path, img_url, ORIG_SIZE, NORM_SIZE, THUMB_SIZE)
    if not upload_response['status']:
        return upload_response

    # Upload data
    original_image = upload_response['original_filename']
    normalized_image = upload_response['normalized_filename']
    thumbnail_image = upload_response['thumbnail_filename']
    original_url = upload_response['original_url']
    normalized_url = upload_response['normalized_url']
    thumbnail_url = upload_response['thumbnail_url']

    # Create Portfolio
    portfolio_created = None
    with db.transaction():
        try:
            portfolio_created = Portfolio.create(site=site,
                                                 title=title,
                                                 description=description,
                                                 original_image=original_image,
                                                 normalized_image=normalized_image,
                                                 thumbnail_image=thumbnail_image)
        except IntegrityError as exp:
            if portfolio_created:
                portfolio_created.delete_instance(IMAGE_PATH)
            else:
                site_img_path = site.get_image_path(IMAGE_PATH)
                if original_image:
                    original_file = os.path.join(site_img_path, original_image)
                    if os.path.exists(original_file):
                        os.remove(original_file)
                if normalized_image:
                    normalized_file = os.path.join(site_img_path, normalized_image)
                    if os.path.exists(normalized_file):
                        os.remove(normalized_file)
                if thumbnail_image:
                    thumbnail_file = os.path.join(site_img_path, thumbnail_image)
                    if os.path.exists(thumbnail_file):
                        os.remove(thumbnail_file)
            # Return error
            return dict(status=False, info='%s' % exp)

    # Lista de portfolios atualizada
    try:
        portfolio_list = template('portfolios_admin_list.html', site=site, host=host, csrf=csrf, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Adicionado com sucesso', portfolio_id=portfolio_created.get_id(),
                original=original_url, normalized=normalized_url, thumbnail=thumbnail_url,
                portfolio_list=portfolio_list)


@route('/portfolio/delete/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_portfolios', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def portfolio_delete(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Delete portfolio post url
    """

    # POST parameters
    site_id = int(request.POST.get('site'))
    user_id = int(request.POST.get('user'))
    portfolio_id = int(request.POST.get('portfolio'))

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Delete portfolio
    site_img_path = site.get_image_path(IMAGE_PATH)
    portfolio.delete_all(site_img_path)

    # Images url
    img_url = '%s/%s/' % (host, IMAGE_DIR)

    # Lista de portfolios atualizada
    try:
        portfolio_list = template('portfolios_admin_list.html', site=site, host=host, csrf=csrf, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Apagado com sucesso', portfolio_id=portfolio_id, portfolio_list=portfolio_list)


@route('/portfolio/update/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_portfolios', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def portfolio_update(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Edit portfolio post url
    """

    # POST parameters
    site_id = int(request.POST.get('site'))
    user_id = int(request.POST.get('user'))
    portfolio_id = int(request.POST.get('portfolio'))
    title = request.POST.get('title')
    description = request.POST.get('description')

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Update upload portfolio image
    if request.files.get('upload'):
        img_path = site.get_image_path(IMAGE_PATH)
        original_file = os.path.join(img_path, portfolio.original_image)
        normalized_file = os.path.join(img_path, portfolio.normalized_image)
        thumbnail_file = os.path.join(img_path, portfolio.thumbnail_image)
        upload_response = upload_image(request, original_file, normalized_file, thumbnail_file, ORIG_SIZE, NORM_SIZE, THUMB_SIZE)
        if not upload_response['status']:
            return upload_response

    # Upload data
    portfolio.title = title
    portfolio.description = description
    portfolio.save()

    # Images data
    img_url = '%s/%s/' % (host, IMAGE_DIR)
    original_url = img_url + portfolio.original_image
    normalized_url = img_url + portfolio.normalized_image
    thumbnail_url = img_url + portfolio.thumbnail_image

    # Lista de portfolios atualizada
    try:
        portfolio_list = template('portfolios_admin_list.html', site=site, host=host, csrf=csrf, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Atualizado com sucesso', portfolio_id=portfolio.get_id(),
                original=original_url, normalized=normalized_url, thumbnail=thumbnail_url,
                portfolio_list=portfolio_list)
