"""
Provides the file storage implementation for the ORM. Provides
corresponding value classes, column classes and models generators
for very common cases.
"""

from typing import *
import datetime
from sqlalchemy import types
from .types import BigAutoIncrement, Column, DateTime, Integer, String
from .model import DatabaseModel
from ... import config, defaults
from ...tools import get_calling_app


__all__ = [
    'StoredFile',
    'StoredImage',
    'File',
    'Image',
    'files_model',
    'images_model',
]


class StoredFile:
    """
    The VALUE class which will be used to represent the column' value
    of the stored file.
    """

    def __init__(self, entity: str, file_id: str):
        self.entity: str = entity
        self.file_id: str = file_id

    @property
    def url(self) -> str:
        """ Returns the ready to use URL for the stored file. This URL may be
        used by any frontend component to download (fetch) fiven file.
        """

        if self.file_id.startswith('/'):
            return f"{defaults.URL_STATICS}/assets/{self.file_id.lstrip('/')}"
        return f"{defaults.URL_FILES}/{self.entity}/{self.file_id}"


class StoredImage(StoredFile):
    """
    The VALUE class which will be used to represent the column' value
    of the stored image.
    """
    pass


class File(types.TypeDecorator):
    """
    The COLUMN class used when declaring the corresponding attribute in the
    ORM model. Represents the file storage facility with the database projection,
    storing both file contents to the file storage (identified by the given
    entity name) and the record about that uploaded file into the corresponding
    model attribute (and corresponding row column at the database side).

    Example of usage:

    ``
    # For example, we have registered storage entity 'all_files' and the parent
    # application is 'just_test'.

    class MyModel(ds.Model):
        id = ds.UUIDPrimaryKey()
        ...
        uploaded_file = ds.Column(ds.File('just_test.all_files'))
    ``

    Note that if the application name is omitted in the entity name - the
    current (calling) application will be used by default.
    """

    impl = types.String
    cache_ok = True

    def __init__(self, entity: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if '.' not in entity:
            entity = '.'.join([get_calling_app(), entity])

        self.length: int = 255
        self.entity: str = entity

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return None if value is None else StoredFile(self.entity, value)


class Image(types.TypeDecorator):
    """
    The COLUMN class used when declaring the corresponding attribute in the
    ORM model. Represents the image storage facility with the database projection,
    storing both image contents to the file storage (identified by the given
    entity name) and the record about that uploaded image into the corresponding
    model attribute (and corresponding row column at the database side).

    Example of usage:

    ``
    # For example, we have registered storage entity 'all_files' and the parent
    # application is 'just_test'.

    class MyModel(ds.Model):
        id = ds.UUIDPrimaryKey()
        ...
        uploaded_file = ds.Column(ds.Image('just_test.all_files'))
    ``

    Note that if the application name is omitted in the entity name - the
    current (calling) application will be used by default.
    """

    impl = types.String
    cache_ok = True

    def __init__(self, entity: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if '.' not in entity:
            entity = '.'.join([get_calling_app(), entity])

        self.length: int = 255
        self.entity: str = entity

    def process_literal_param(self, value, dialect):
        return value

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return None if value is None else StoredImage(self.entity, value)


class _FilesModelMixin:
    """
    The private mixin class used for automated storage model generator.
    """

    id = BigAutoIncrement()
    """ The primary key. """

    created_at = Column(DateTime(), default=datetime.datetime.today)
    """ The timestamp when this file object been uploaded. Defaults to
    the current date and time (to the ``now``). """

    sort = Column(Integer(), nullable=False, default=0)
    """ The column which provides the sorting facility of the uploaded
    file amont other corresponding records. """

    caption = Column(String(255), nullable=False, default='')
    """ The human readable name (caption) of the uploaded file object. """

    @property
    def url(self):
        """ Returns the ready to use URL for the stored file. This URL may be
        used by any frontend component to download (fetch) fiven file.
        """

        file: Optional[StoredFile] = getattr(self, 'file')
        return None if file is None else file.url

    # @property
    # def filesize(self):
    #     file_id: Optional[str] = getattr(self, 'file')
    #     if not file_id:
    #         return None
    #     os.path.getsize(get_abs_filename(file_id))


class _ImagesModelMixin(_FilesModelMixin):
    pass


def files_model(
        name: str,
        entity: str,
        sort_by_time: bool = False,
        sort_desc: bool = False,
        requires: Optional[Union[str, List[str]]] = None
):
    """ Generates a new :class:`~wefram.ds.Model`` for storing files. The new
    model will have next set of attributes:

    * ``id``: ``BigAutoIncrement`` column primary key;
    * ``created_at``: ``DateTime`` column which automatically set to the
        file's upload date & time;
    * ``sort``: ``Integer`` column, which may be used to sort files;
    * ``caption``: ``String`` column, storing the uploaded file/document name;
    * ``file``: ``StoredFile`` column, which contains the actual uploaded ``file_id``;

    """

    from ... import api

    app: str = get_calling_app()
    if '.' not in entity:
        entity = '.'.join([app, entity])
    cls: ClassVar = type(name, (_FilesModelMixin, DatabaseModel,), {
        '__app__': app,
        'file': Column(File(entity)),
    })
    secondary_order = \
        (getattr(cls, 'created_at').desc() if sort_desc else getattr(cls, 'created_at')) \
        if sort_by_time \
        else (getattr(cls, 'id').desc() if sort_desc else getattr(cls, 'id'))
    getattr(cls, 'Meta').order = [
        (getattr(cls, 'sort').desc() if sort_desc else getattr(cls, 'sort')),
        secondary_order
    ]

    api.register(type(name, (api.FilesModelAPI,), {
        'model': cls,
        'requires': requires,
        'storage_entity': entity
    }))

    return cls


def images_model(
        name: str,
        entity: str,
        sort_by_time: bool = False,
        sort_desc: bool = False,
        requires: Optional[Union[str, List[str]]] = None
):
    """ Generates a new :class:`~wefram.ds.Model`` for storing images. The new
    model will have next set of attributes:

    * ``id``: ``BigAutoIncrement`` column primary key;
    * ``created_at``: ``DateTime`` column which automatically set to the
        file's upload date & time;
    * ``sort``: ``Integer`` column, which may be used to sort files;
    * ``caption``: ``String`` column, storing the uploaded file/document name;
    * ``file``: ``StoredImage`` column, which contains the actual uploaded ``file_id``;

    """

    from ... import api

    app: str = get_calling_app()
    if '.' not in entity:
        entity = '.'.join([app, entity])
    cls: ClassVar = type(name, (_ImagesModelMixin, DatabaseModel,), {
        '__app__': app,
        'file': Column(Image(entity)),
    })
    secondary_order = \
        (getattr(cls, 'created_at').desc() if sort_desc else getattr(cls, 'created_at')) \
        if sort_by_time \
        else (getattr(cls, 'id').desc() if sort_desc else getattr(cls, 'id'))
    getattr(cls, 'Meta').order = [
        (getattr(cls, 'sort').desc() if sort_desc else getattr(cls, 'sort')),
        secondary_order
    ]

    api.register(type(name, (api.ImagesModelAPI,), {
        'model': cls,
        'requires': requires,
        'storage_entity': entity
    }))

    return cls

