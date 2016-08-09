"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
import os
import sys
import re
from importlib import import_module
import smtplib
from threading import Thread
from PIL import Image

from email.header import make_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate, formataddr


__author__ = 'João Neto'


def import_modules(modules_path):
    """
    Import modules from dir
    Magic is here!!!!
    """

    sys.path.append(modules_path)
    modules_list = []
    for file_name in os.listdir(modules_path):
        name, ext = os.path.splitext(file_name)
        if ext == '.py':
            opcms_module = import_module(name)
            modules_list.append(opcms_module)
    return modules_list


def import_templates(templates_path):
    """
    Import templates from dir
    Magic is here!!!!
    """

    sys.path.append(templates_path)
    templates_dict = {}
    for dir_name in os.listdir(templates_path):
        template_dir = os.path.join(templates_path, dir_name)
        if os.path.isdir(template_dir):
            template_py = os.path.join(template_dir, 'template.py')
            if os.path.exists(template_py):
                template_module = import_module(dir_name + '.template')
                templates_dict[template_module.short_name] = template_module

    return templates_dict


class Regex():
    user = lambda s: re.compile(
        "^[a-z0-9_]{3,32}$"
    ).match(s) is not None

    email = lambda s: re.compile(
        "^([\da-z])([a-z0-9_\.-]+)@([\da-z])([\da-z\.-]+)\.([a-z]{2,6})$"
    ).match(s) is not None

    phone_number = lambda s: re.compile(
        "^(\([1-9]{2}\)[0-9]{4,5}-[0-9]{4}[,]?)+$"
    ).match(s) is not None

    map_url = lambda s: re.compile(
        "^(http)[s]?://([\da-z])([\da-z\.-]+)\.([a-z]{2,6})(/[a-zA-Z0-9_\.-/?%&=]*)+$"
    ).match(s) is not None

    facebook_url = lambda s: re.compile(
        "^(http)[s]?://(www|[a-zA-Z]{2}-[a-zA-Z]{2})\.facebook\.com/(pages/[a-zA-Z0-9_\.-]+/[0-9]+|[a-zA-Z0-9\.-]+)[/]?$"
    ).match(s) is not None

    twitter_url = lambda s: re.compile(
        "^(http)[s]?://twitter\.com/(#!/)?[a-zA-Z0-9_]{1,15}[/]?$"
    ).match(s) is not None


def send_email_simple(sender, receiver, subject, text, html, attachments=()):
    """
    send_email simple function
    """
    charset = "UTF-8"

    msg = MIMEMultipart('related')

    msg['From'] = str(make_header([(sender, charset)]))
    msg['To'] = str(make_header([(receiver, charset)]))
    msg['Subject'] = str(make_header([(subject, charset)]))
    msg['Date'] = formatdate()

    body = MIMEMultipart('alternative')
    plain_part = MIMEText(text, 'plain', charset)
    plain_part.add_header('Content-Disposition', 'inline')
    html_part = MIMEText(html, 'html', charset)
    html_part.add_header('Content-Disposition', 'inline')
    body.attach(plain_part)
    body.attach(html_part)

    msg.attach(body)

    for filename, cid in attachments:
        fp = open(filename, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        if cid:
            img.add_header('Content-ID', '<%s>' % cid)
            img.add_header('Content-Disposition', 'inline')
        else:
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
        msg.attach(img)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()


def send_email(sender, receiver, subject, text, html, attachments=()):
    t = Thread(target=send_email_simple, args=(sender, receiver, subject, text, html, attachments))
    t.start()


def send_recovery_email(host, sender, user):
    recovery_url = "%s/user/recovery/%s/%s/" % (host, user.get_id(), user.user_hash)
    receiver = formataddr((user.name, user.email), 'UTF-8')
    subject = "Recuperação de senha"
    text = """\
    Acesse o link para recuperar sua senha:

    %s
    """ % recovery_url
    html = """\
    <html>
      <head></head>
      <body>
        <p>Acesse o link para recuperar sua senha:</p>
        <p><a href="%s">Recuperar Senha</a></p>
      </body>
    </html>
    """ % recovery_url
    attachments = []
    send_email(sender, receiver, subject, text, html, attachments)


def send_contact_email(host, name, email, site, subject_message, message):
    sender = formataddr((name, email), 'UTF-8')
    receiver = formataddr((site.site_owner, site.site_email), 'UTF-8')
    subject = "Formulário de Contato %s" % host
    text = """\
    Enviado por: "%s" <%s>
    Assunto: %s
    Mensagem:

    %s
    """ % (name, email, subject_message, message)
    html_message = message.replace("\r\n", "<br/>").replace("\n", "<br/>")
    html = """\
    <html>
      <head></head>
      <body>
        <p>Enviado por: "%s" &lt;%s&gt;</p>
        <p>Assunto: %s</p>
        <p>Mensagem:</p>
        <p>%s</p>
      </body>
    </html>
    """ % (name, email, subject_message, html_message)
    attachments = []
    send_email(sender, receiver, subject, text, html, attachments)


def upload_image(request, original_file, normalized_file, thumbnail_file, orig_size, norm_size, thumb_size):
    # Upload image info
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename.lower())
    if ext not in ('.jpg', '.jpeg'):
        return dict(status=False, info='Tipo de arquivo não suportado')

    # Save original file
    try:
        with upload.file as f:
            im = Image.open(f)

            # Check the original size
            im_w, im_h = im.size
            orig_w, orig_h = orig_size
            if (im_w < orig_w) and (im_h < orig_h):
                return dict(status=False, info='Imagem deve ter largura >= %d ou altura >= %d' % (orig_w, orig_h))

            # Save original file with ANTIALIAS
            im.thumbnail(orig_size, Image.ANTIALIAS)
            im.save(original_file, "JPEG")
    except IOError:
        if os.path.exists(original_file):
            os.remove(original_file)
        if os.path.exists(normalized_file):
            os.remove(normalized_file)
        if os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
        return dict(status=False, info='Não foi possivel criar imagem')

    # Resize and save normalized image
    try:
        with open(original_file, "rb") as f:
            im = Image.open(f)
            im.thumbnail(norm_size, Image.ANTIALIAS)
            im.save(normalized_file, "JPEG")
    except IOError:
        if os.path.exists(original_file):
            os.remove(original_file)
        if os.path.exists(normalized_file):
            os.remove(normalized_file)
        if os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
        return dict(status=False, info='Não foi possivel criar imagem')

    # Resize and save thumbnail image
    try:
        with open(original_file, "rb") as f:
            im = Image.open(f)
            im.thumbnail(thumb_size, Image.ANTIALIAS)
            im.save(thumbnail_file, "JPEG")
    except IOError:
        if os.path.exists(original_file):
            os.remove(original_file)
        if os.path.exists(normalized_file):
            os.remove(normalized_file)
        if os.path.exists(thumbnail_file):
            os.remove(thumbnail_file)
        return dict(status=False, info='Não foi possivel criar imagem')

    # return OK
    return dict(status=True, info='Imagem atualizada com sucesso')


def upload_new_image(request, img_prefix, start_index, img_path, img_url, orig_size, norm_size, thumb_size):
    # Upload image info
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename.lower())
    if ext not in ('.jpg', '.jpeg'):
        return dict(status=False, info='Tipo de arquivo não suportado')

    # Create new file names for images
    index = start_index
    original_file = os.path.join(img_path, "%s%d.jpg" % (img_prefix, index))
    normalized_file = os.path.join(img_path, "%s%d_norm.jpg" % (img_prefix, index))
    thumbnail_file = os.path.join(img_path, "%s%d_thumb.jpg" % (img_prefix, index))
    while os.path.exists(original_file) or os.path.exists(thumbnail_file) or os.path.exists(normalized_file):
        index += 1
        original_file = os.path.join(img_path, "%s%d.jpg" % (img_prefix, index))
        normalized_file = os.path.join(img_path, "%s%d_norm.jpg" % (img_prefix, index))
        thumbnail_file = os.path.join(img_path, "%s%d_thumb.jpg" % (img_prefix, index))

    # Upload images
    upload_response = upload_image(request, original_file, normalized_file, thumbnail_file, orig_size, norm_size, thumb_size)
    if not upload_response['status']:
        return upload_response

    # Response data
    original_filename = os.path.split(original_file)[1]
    normalized_filename = os.path.split(normalized_file)[1]
    thumbnail_filename = os.path.split(thumbnail_file)[1]
    original_url = img_url + original_filename
    normalized_url = img_url + normalized_filename
    thumbnail_url = img_url + thumbnail_filename

    # return OK
    return dict(status=True,
                info='Imagem salva com sucesso',
                original_filename=original_filename,
                normalized_filename=normalized_filename,
                thumbnail_filename=thumbnail_filename,
                original_url=original_url,
                normalized_url=normalized_url,
                thumbnail_url=thumbnail_url)
