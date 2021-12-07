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
    storage_entity: str = None

    @classmethod
    async def create(cls, **with_values) -> Union[bool, object]:
        if 'file' in with_values and isinstance(with_values['file'], UploadFile):
            file: UploadFile = with_values['file']
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
    pass
