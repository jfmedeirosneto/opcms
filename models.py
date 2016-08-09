"""
opcms One Page Content Management System
https://github.com/jfmedeirosneto/opcms
Copyright(c) 2016 João Neto <jfmedeirosneto@yahoo.com.br>
"""
from datetime import datetime
from hashlib import sha256
import os

from peewee import SqliteDatabase, Model, BooleanField, CharField, ForeignKeyField, IntegrityError, \
    TextField

from utils import Regex


__author__ = 'João Neto'

# Database
# To configure database check peewee documentation
# http://docs.peewee-orm.com/en/latest/peewee/database.html
db = SqliteDatabase('database.sqlite')


# Print all queries of peewee to stderr.
# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


class BaseModel(Model):
    active = BooleanField(default=False,
                          verbose_name='Registro ativo',
                          help_text='Indica se registro está ativo')
    created_date = CharField(default=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                             verbose_name='Data criação',
                             help_text='Indica data de criação desse registro')
    modified_date = CharField(default=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                              verbose_name='Data modificação',
                              help_text='Indica data de modificação desse registro')

    def save(self, force_insert=False, only=None):
        self.modified_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        super(BaseModel, self).save(force_insert, only)

    def get_dictionary(self):
        data = {}
        for field_name, field in zip(self._meta.sorted_field_names, self._meta.sorted_fields):
            field_name = field.name
            if isinstance(field, ForeignKeyField):
                data[field_name] = getattr(self, field_name).get_id()
            else:
                data[field_name] = getattr(self, field_name)
        return data

    def get_fields(self):
        return self._meta.sorted_fields

    class Meta:
        database = db


class User(BaseModel):
    email = CharField(unique=True,
                      verbose_name='Email pessoal',
                      help_text='Coloque seu email pessoal')
    password = CharField(verbose_name='Senha',
                         help_text='Coloque a senha para login')
    name = CharField(verbose_name='Nome completo',
                     help_text='Coloque sem nome completo')
    user_hash = CharField(default='',
                          verbose_name='Hash',
                          help_text='Hash')

    def save(self, force_insert=False, only=None):
        if not Regex.email(self.email):
            raise IntegrityError('Email inválido')
        str_hash = self.email + datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.user_hash = sha256(str_hash.encode()).hexdigest()
        super(User, self).save(force_insert, only)

    def __str__(self):
        return '\'%s\' <%s>' % (self.name, self.email)


class Site(BaseModel):
    user = ForeignKeyField(User,
                           related_name='sites',
                           verbose_name='Proprietário do site',
                           help_text='Indica o proprietário desse site')
    site_email = CharField(unique=True,
                           default='',
                           verbose_name='Email do site',
                           help_text='Coloque o email do site')
    site_owner = CharField(default='Minha Nova Empresa',
                           verbose_name='Nome da empresa/profissional',
                           help_text='Coloque o nome da sua empresa/profissional')
    site_template = CharField(default='agency',
                              verbose_name='Template do site',
                              help_text='Selecione o template do site')
    site_title = CharField(default='Meu Novo Site',
                           verbose_name='Título do site',
                           help_text='Coloque o título do site')
    site_description = TextField(default='Um Site Onde Tudo é Novo.<br>Amamos Inovação!',
                                 verbose_name='Descrição do site',
                                 help_text='Coloque uma descrição do site')
    site_copyright = CharField(default='Copyright © Meu Novo Site %d' % datetime.now().year,
                               verbose_name='Copyright do site',
                               help_text='Coloque o copyright do site')
    page_title = CharField(default='Sobre Esse Novo Site',
                           verbose_name='Título da página principal',
                           help_text='Coloque o título da página principal')
    page_content = TextField(
        default='Um Site Construído Por Pessoas Que Amam o Novo.<br>Você Ama o Novo?<br/>Então Aqui é o Seu Lugar!',
        verbose_name='Conteúdo da página principal',
        help_text='Coloque o conteúdo da página principal')
    address = TextField(default='Rua Inovadores, 2015, Centro<br>Jaraguá do Sul, SC 89250-000',
                        verbose_name='Endereço da empresa/profissional',
                        help_text='Coloque o endereço da  empresa/profissional')
    map_url = CharField(default='https://goo.gl/maps/Fxpy9',
                        verbose_name='URL do endereço',
                        help_text='Coloque uma URL de mapa para o endereço da empresa/profissional')
    phones = CharField(default='(12)1234-1234,',
                       verbose_name='Telefones da empresa/profissional',
                       help_text='Coloque os telefones da empresa/profissional (separados por vírgula)')
    whats_app_phones = CharField(default='(12)1234-1234,',
                                 verbose_name='Telefones WhatsApp da empresa/profissional',
                                 help_text='Coloque os telefones WhatsApp da empresa/profissional (separados por vírgula)')
    facebook_url = CharField(default='https://www.facebook.com/facebook',
                             verbose_name='URL do Facebook',
                             help_text='Coloque uma URL da página/perfil do Facebook')
    twitter_url = CharField(default='https://twitter.com/twitter',
                            verbose_name='URL do Twitter',
                            help_text='Coloque uma URL do perfil do Twitter')


    def get_image_path(self, img_path):
        """
        :return Path of site images
        """
        img_user_dir = 'site%d' % self.get_id()
        site_img_path = os.path.join(img_path, img_user_dir)
        if not os.path.exists(site_img_path):
            os.makedirs(site_img_path)
        return site_img_path


    def save(self, force_insert=False, only=None):
        if not Regex.email(self.site_email):
            raise IntegrityError('Email inválido')
        if not Regex.map_url(self.map_url):
            raise IntegrityError('URL do endereço inválido')
        if not Regex.phone_number(self.phones):
            raise IntegrityError('Telefones inválidos')
        if not Regex.phone_number(self.whats_app_phones):
            raise IntegrityError('Telefones WhatsApp inválidos')
        if not Regex.facebook_url(self.facebook_url):
            raise IntegrityError('Facebook inválido')
        if not Regex.twitter_url(self.twitter_url):
            raise IntegrityError('Twitter inválido')
        super(Site, self).save(force_insert, only)


class Portfolio(BaseModel):
    site = ForeignKeyField(Site,
                           related_name='portfolios',
                           verbose_name='Site do portfólio',
                           help_text='Indica o site desse portfólio')
    title = CharField(default='Portfólio',
                      verbose_name='Título do portfólio',
                      help_text='Coloque o título do portfólio')
    description = TextField(default='Portfólio',
                            verbose_name='Descrição do portfólio',
                            help_text='Coloque uma descrição do portfólio')
    original_image = CharField(unique=True,
                               verbose_name='Imagem original',
                               help_text='Imagem original')
    normalized_image = CharField(unique=True,
                                 verbose_name='Imagem normalizada',
                                 help_text='Imagem normalizada')
    thumbnail_image = CharField(unique=True,
                                verbose_name='Imagem reduzida',
                                help_text='Imagem reduzida')

    def delete_all(self, site_img_path):
        # Delete pictures data
        for picture in self.pictures:
            picture.delete_all(site_img_path)

        # Delete own data
        if self.original_image:
            original_file = os.path.join(site_img_path, self.original_image)
            if os.path.exists(original_file):
                os.remove(original_file)
        if self.normalized_image:
            normalized_file = os.path.join(site_img_path, self.normalized_image)
            if os.path.exists(normalized_file):
                os.remove(normalized_file)
        if self.thumbnail_image:
            thumbnail_file = os.path.join(site_img_path, self.thumbnail_image)
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)
        super(Portfolio, self).delete_instance()

    def save(self, force_insert=False, only=None):
        super(Portfolio, self).save(force_insert, only)


class Picture(BaseModel):
    site = ForeignKeyField(Site,
                           related_name='pictures',
                           verbose_name='Site da imagem',
                           help_text='Indica o site dessa imagem')
    portfolio = ForeignKeyField(Portfolio,
                                related_name='pictures',
                                verbose_name='Portfólio da imagem',
                                help_text='Indica o portfólio dessa imagem')
    title = CharField(default='Imagem',
                      verbose_name='Título da imagem',
                      help_text='Coloque o título da imagem')
    description = TextField(default='Imagem',
                            verbose_name='Descrição da imagem',
                            help_text='Coloque uma descrição da imagem')
    original_image = CharField(unique=True,
                               verbose_name='Imagem original',
                               help_text='Imagem original')
    normalized_image = CharField(unique=True,
                                 verbose_name='Imagem normalizada',
                                 help_text='Imagem normalizada')
    thumbnail_image = CharField(unique=True,
                                verbose_name='Imagem reduzida',
                                help_text='Imagem reduzida')

    def delete_all(self, site_img_path):
        if self.original_image:
            original_file = os.path.join(site_img_path, self.original_image)
            if os.path.exists(original_file):
                os.remove(original_file)
        if self.normalized_image:
            normalized_file = os.path.join(site_img_path, self.normalized_image)
            if os.path.exists(normalized_file):
                os.remove(normalized_file)
        if self.thumbnail_image:
            thumbnail_file = os.path.join(site_img_path, self.thumbnail_image)
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)
        super(Picture, self).delete_instance()

    def save(self, force_insert=False, only=None):
        super(Picture, self).save(force_insert, only)


# Connect to db and create tables
db.connect()
db.create_tables([User, Site, Portfolio, Picture], safe=True)