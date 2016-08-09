import os

from bottle import request, route, view, abort, template
from peewee import IntegrityError

from decorators import require_site_registered, require_site_activated, require_csrf, \
    require_logged_in, require_permissions
from models import Portfolio, Picture, db
from settings import IMAGE_DIR, IMAGE_PATH, ORIG_SIZE, NORM_SIZE, THUMB_SIZE
from utils import upload_new_image, upload_image


__author__ = 'João Neto'


@route('/pictures/admin/<site_id:int>/<user_id:int>/<portfolio_id:int>/', method='GET')
@view('pictures_admin.html')
@require_site_registered()
@require_site_activated()
@require_csrf(token_id='csrf_pictures')
@require_logged_in()
@require_permissions()
def pictures_admin_page(site, host, netloc, csrf, logged_in, user_id_logged_in, site_id, user_id, portfolio_id):
    """
    Admin picutes url
    """

    try:
        # Portfolio
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)

        # Images url
        img_url = '%s/%s/' % (host, IMAGE_DIR)

        # Call template
        return dict(host=host, site=site, csrf=csrf, logged_in=logged_in, user_id_logged_in=user_id_logged_in,
                    portfolio=portfolio, img_url=img_url)
    except Portfolio.DoesNotExist:
        abort(404, 'Portfólio não encontrado')


@route('/picture/get/<site_id:int>/<user_id:int>/<portfolio_id:int>/<picture_id:int>/', method='GET')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_permissions(json_response=True)
def picture_get(site, host, netloc, site_id, user_id, portfolio_id, picture_id):
    """
    Get portfolio url
    """

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Picture
    try:
        picture = Picture.get(Picture.id == picture_id, Picture.site == site, Picture.portfolio == portfolio)
    except Picture.DoesNotExist:
        return dict(status=False, info='Imagem não encontrada')

    # Images data
    site_img_url = '%s/%s/' % (host, IMAGE_DIR)
    original_url = site_img_url + picture.original_image
    normalized_url = site_img_url + picture.normalized_image
    thumbnail_url = site_img_url + picture.thumbnail_image

    # Return OK
    return dict(status=True,
                info='Imagem encontrada com sucesso',
                original=original_url,
                normalized=normalized_url,
                thumbnail=thumbnail_url,
                **picture.get_dictionary())


@route('/picture/add/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_pictures', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def picture_add(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Add picture post url
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

    # Upload picture image
    start_index = 1
    try:
        pictures = site.pictures.order_by(Picture.id.desc())
        last_picture = pictures.get()
        start_index = last_picture.id + 1
    except Picture.DoesNotExist:
        pass
    img_path = site.get_image_path(IMAGE_PATH)
    img_url = '%s/%s/' % (host, IMAGE_DIR)
    upload_response = upload_new_image(request, 'picture', start_index, img_path, img_url, ORIG_SIZE, NORM_SIZE, THUMB_SIZE)
    if not upload_response['status']:
        return upload_response

    # Upload data
    original_image = upload_response['original_filename']
    normalized_image = upload_response['normalized_filename']
    thumbnail_image = upload_response['thumbnail_filename']
    original_url = upload_response['original_url']
    normalized_url = upload_response['normalized_url']
    thumbnail_url = upload_response['thumbnail_url']

    # Create Picture
    picture_created = None
    with db.transaction():
        try:
            picture_created = Picture.create(site=site,
                                             portfolio=portfolio,
                                             title=title,
                                             description=description,
                                             original_image=original_image,
                                             normalized_image=normalized_image,
                                             thumbnail_image=thumbnail_image)
        except IntegrityError as exp:
            if picture_created:
                picture_created.delete_instance(IMAGE_PATH)
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

    # Lista de pictures atualizada
    try:
        picture_list = template('pictures_admin_list.html', site=site, host=host, csrf=csrf,
                                portfolio=portfolio, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Adicionada com sucesso', picture_id=picture_created.get_id(),
                original=original_url, normalized=normalized_url, thumbnail=thumbnail_url,
                picture_list=picture_list)


@route('/picture/delete/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_pictures', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def picture_delete(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Delete picture post url
    """

    # POST parameters
    site_id = int(request.POST.get('site'))
    user_id = int(request.POST.get('user'))
    portfolio_id = int(request.POST.get('portfolio'))
    picture_id = int(request.POST.get('picture'))

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Picture
    try:
        picture = Picture.get(Picture.id == picture_id, Picture.site == site, Picture.portfolio == portfolio)
    except Picture.DoesNotExist:
        return dict(status=False, info='Imagem não encontrada')

    # Delete picture
    site_img_path = site.get_image_path(IMAGE_PATH)
    picture.delete_all(site_img_path)

    # Images url
    img_url = '%s/%s/' % (host, IMAGE_DIR)

    # Lista de pictures atualizada
    try:
        picture_list = template('pictures_admin_list.html', site=site, host=host, csrf=csrf,
                                portfolio=portfolio, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Apagado com sucesso', picture_id=picture_id, picture_list=picture_list)


@route('/picture/update/', method='POST')
@require_site_registered(json_response=True)
@require_site_activated(json_response=True)
@require_csrf(token_id='csrf_pictures', json_response=True)
@require_logged_in(json_response=True)
@require_permissions(json_response=True)
def picture_update(site, host, netloc, csrf, logged_in, user_id_logged_in):
    """
    Edit picture post url
    """

    # POST parameters
    site_id = int(request.POST.get('site'))
    user_id = int(request.POST.get('user'))
    portfolio_id = int(request.POST.get('portfolio'))
    picture_id = int(request.POST.get('picture'))
    title = request.POST.get('title')
    description = request.POST.get('description')

    # Portfolio
    try:
        portfolio = Portfolio.get(Portfolio.id == portfolio_id, Portfolio.site == site)
    except Portfolio.DoesNotExist:
        return dict(status=False, info='Portfólio não encontrado')

    # Picture
    try:
        picture = Picture.get(Picture.id == picture_id, Picture.site == site, Picture.portfolio == portfolio)
    except Picture.DoesNotExist:
        return dict(status=False, info='Imagem não encontrada')

    # Update upload picture image
    if request.files.get('upload'):
        img_path = site.get_image_path(IMAGE_PATH)
        original_file = os.path.join(img_path, picture.original_image)
        normalized_file = os.path.join(img_path, picture.normalized_image)
        thumbnail_file = os.path.join(img_path, picture.thumbnail_image)
        upload_response = upload_image(request, original_file, normalized_file, thumbnail_file, ORIG_SIZE, NORM_SIZE, THUMB_SIZE)
        if not upload_response['status']:
            return upload_response

    # Upload data
    picture.title = title
    picture.description = description
    picture.save()

    # Images data
    img_url = '%s/%s/' % (host, IMAGE_DIR)
    original_url = img_url + picture.original_image
    normalized_url = img_url + picture.normalized_image
    thumbnail_url = img_url + picture.thumbnail_image

    # Lista de pictures atualizada
    try:
        picture_list = template('pictures_admin_list.html', site=site, host=host, csrf=csrf,
                                portfolio=portfolio, img_url=img_url)
    except Exception as exp:
        return dict(status=False, info='%s' % exp)

    # Return OK
    return dict(status=True, info='Atualizada com sucesso', picture_id=picture.get_id(),
                original=original_url, normalized=normalized_url, thumbnail=thumbnail_url,
                picture_list=picture_list)
