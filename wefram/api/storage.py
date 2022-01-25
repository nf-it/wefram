"""
Provides the file storage API. Used to simplify dealing with storage entities like
uploaded files & images via the platform API.
"""

from typing import *
import os.path
from starlette.datastructures import UploadFile
from .models import ModelAPI
from .mixins import SortedModelMixin
from ..l10n import gettext
from .. import ds, logger, exceptions


__all__ = [
    'FilesModelAPI',
    'ImagesModelAPI'
]


class FilesModelAPI(SortedModelMixin, ModelAPI):
    """
    The special case of EntityAPI class, providing the file storage handling
    via the platform API. There are two base approachs on how to use this
    class:

    (1) By inheriting from it, for example:

    .. highlight:: python
    .. code-block:: python

        from wefram import api

        @api.register
        class MyFiles(api.FilesModelAPI):
            storage_entity: str = 'my_entity'

    (2) By using API model generator (several predefined, for common cases, are
    included in the platform):

    .. highlight:: python
    .. code-block:: python

        from wefram import ds

        # Creates the MyFiles data storage class and declare the corresponding
        # API entity automatically for you.
        MyFiles = ds.files_model(...)

    Note that the second case directs us not to the ``api`` module, but takes
    the function from the ``ds`` module instead. Read more on function
    :py:func:`wefram.ds.files_model`.
    """

    storage_entity: str = None
    """ The corresponding storage entity used to upload and get files. """

    @classmethod
    async def create(cls, **with_values) -> Union[bool, object]:
        """ Handles both single and multiple files upload operation, storing uploaded
        files in the corresponding storage entity.
        """

        # If several files are uploading - the ``is_multiple_file_upload`` form field
        # expected to be specified with value "true" for it. This indicates that there
        # are more than one file is uploading.
        if 'is_multiple_file_upload' in with_values \
                and isinstance(with_values['is_multiple_file_upload'], str) \
                and with_values['is_multiple_file_upload'] == 'true':
            for form_name, form_value in with_values.items():
                if not form_name.startswith('file_upload_data_'):
                    continue
                file: UploadFile = form_value
                file_id: str = ds.storages.upload_file_content(
                    cls.storage_entity,
                    file.file,
                    file.filename,
                    {
                        'content_type': file.content_type
                    }
                )
                await super().create(
                    caption=os.path.splitext(file.filename)[0],
                    file=file_id
                )
            return True

        # Else, handles single file upload.
        elif 'file_upload_data' in with_values and isinstance(with_values['file_upload_data'], UploadFile):
            file: UploadFile = with_values['file_upload_data']
            file_id: str = ds.storages.upload_file_content(
                cls.storage_entity,
                file.file,
                file.filename,
                {
                    'content_type': file.content_type
                }
            )
            with_values.setdefault('caption', os.path.splitext(file.filename)[0])
            with_values['file'] = file_id
        return await super().create(**with_values)

    async def update(self, *keys: [str, int], **values) -> None:
        """ Handles the file update, including file upload (replace). There are two possible
        data formats allowed: JSON and FormData. The first approach provides only existing
        file properties update (for example, file rename). The second one, in addition, provides
        posibility to replace the existing file with the new one.
        """

        if 'file' in values and len(keys) > 1:
            # Diallow to update several records with file uploading or set.
            raise exceptions.ApiError(
                details=gettext("Updating both values and file attachment(s) of the object is not supported", 'system.messages')
            )
        file: UploadFile = values.get('file', None)
        if file is not None:
            file_id: str = ds.storages.upload_file_content(
                self.storage_entity,
                file.file,
                file.filename,
                {
                    'content_type': file.content_type
                }
            )
            values.setdefault('caption', os.path.splitext(file.filename)[0])
            values['file'] = file_id
        keys: List[int] = [int(k) for k in keys]
        await super().update(*keys, **values)

    async def delete(self, *keys: [str, int]) -> None:
        """ Handles the file deletion. """

        keys: List[int] = [int(k) for k in keys]
        items: List[ClassVar[ds.Model]] = await self.model.all(self.model.id.in_(keys))
        for item in items:
            file: str = item.file
            if file is None:
                continue
            if not isinstance(file, ds.StoredFile):
                continue
            if file.file_id.startswith('/'):
                continue
            logger.debug(
                f"removing file with id '{file.file_id}' from '{self.storage_entity}'"
            )
            ds.storages.remove_file(self.storage_entity, file.file_id)
        await super().delete(*keys)


class ImagesModelAPI(FilesModelAPI):
    """
    The same as :py:class:`~wefram.api.FilesModelAPI` class, but for handling images.
    """
    pass
