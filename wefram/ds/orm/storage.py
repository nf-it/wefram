from typing import *
import datetime
from sqlalchemy import types
from .types import BigAutoIncrement, Column, DateTime, Integer, String
from .model import DatabaseModel
from ... import config
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
    def __init__(self, entity: str, file_id: str):
        self.entity: str = entity
        self.file_id: str = file_id

    @property
    def url(self) -> str:
        if self.file_id.startswith('/'):
            return f"{config.STATICS_URL}/assets/{self.file_id.lstrip('/')}"
        return f'{config.FILES_URL}/{self.entity}/{self.file_id}'


class StoredImage(StoredFile):
    pass


class File(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def __init__(self, entity: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length: int = 255
        self.entity: str = entity

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return None if value is None else StoredFile(self.entity, value)


class Image(types.TypeDecorator):
    impl = types.String
    cache_ok = True

    def __init__(self, entity: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length: int = 255
        self.entity: str = entity

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return None if value is None else StoredImage(self.entity, value)


class _FilesModelMixin:
    id = BigAutoIncrement()
    created_at = Column(DateTime(), default=datetime.datetime.today)
    sort = Column(Integer(), nullable=False, default=0)
    caption = Column(String(255), nullable=False, default='')

    @property
    def url(self):
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
    """ Generates a new ds.Model for storing files.
    The new model will have next attributes:
        id: BigAutoIncrement
        created_at: DateTime which automatically set to the file
            upload date & time
        sort: Integer, which may be used to sort files
        caption: String, storing the uploaded file/document name
        file: StoredFile, which contains the actual uploaded
            file ID
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

