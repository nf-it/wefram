from typing import *
from uuid import uuid4
import os
import json
import shutil
import datetime
import rfc6266
import anyio
from starlette.datastructures import URL, Headers
from email.utils import parsedate
from ...requests import FileResponse, Request, NotModifiedResponse
from ... import config, exceptions
from . import entities


__all__ = [
    'FilenameParts',
    'upload_file_content',
    'remove_file',
    'remove_files',
    'get_file_response',
    'get_abs_filename'
]


FilenameParts = Tuple[str, str, str]


def uuid_from(src: str) -> str:
    return src.replace('-', '')


def file_not_modified(
        response_headers: Headers,
        request_headers: Headers
) -> bool:
    try:
        if_none_match = request_headers["if-none-match"]
        etag = response_headers["etag"]
        if if_none_match == etag:
            return True
    except KeyError:
        pass

    try:
        if_modified_since = parsedate(request_headers["if-modified-since"])
        last_modified = parsedate(response_headers["last-modified"])
        if (
                if_modified_since is not None
                and last_modified is not None
                and if_modified_since >= last_modified
        ):
            return True
    except KeyError:
        pass

    return False


def test_required(entity_name: str) -> bool:
    from ...aaa import permitted

    if entity_name not in entities.registered:
        return False

    entity: entities.StorageEntity = entities.registered[entity_name]
    if not entity.requires:
        return True
    requires: List[str] = list(entity.requires) if isinstance(entity.requires, (list, tuple)) else [entity.requires]
    requires = [(
        r if '.' in r else '.'.join([entity.app, r])
    ) for r in requires]
    return permitted(requires)


def test_readable(entity_name: str) -> bool:
    from ...aaa import permitted
    if entity_name not in entities.registered:
        return False
    entity: entities.StorageEntity = entities.registered[entity_name]
    if not entity.readable:
        return True
    return permitted(entity.readable)


def get_file_subpath(file_id: str) -> FilenameParts:
    return file_id[:2], file_id[2:4], file_id[4:]


def get_file_root(entity: str, file_id: str) -> str:
    return os.path.join(config.FILES_ROOT, entity, file_id[:2])


def get_file_blobfn(entity: str, file_id: str, filename: str) -> str:
    dir1, dir2, dir3 = get_file_subpath(file_id)
    return os.path.join(config.FILES_ROOT, entity, dir1, dir2, dir3, filename)


def get_file_infofn(entity: str, file_id: str) -> str:
    dir1, dir2, dir3 = get_file_subpath(file_id)
    return os.path.join(config.FILES_ROOT, entity, dir1, dir2, dir3, '.fileinfo.json')


def upload_file_content(
        entity: str,
        file: Any,
        filename: str,
        info: Optional[dict] = None,
        force_id: Optional[str] = None
) -> str:
    from ...aaa import get_current_user

    if not test_required(entity):
        raise exceptions.AccessDenied()

    new_file_id: str = uuid_from(uuid4().hex if not force_id else force_id)
    dir1: str
    dir2: str
    subn: str
    dir1, dir2, dir3 = get_file_subpath(new_file_id)
    os.makedirs(os.path.join(config.FILES_ROOT, entity, dir1, dir2, dir3))
    blobfn: str = get_file_blobfn(entity, new_file_id, filename)
    infofn: str = get_file_infofn(entity, new_file_id)

    with open(blobfn, 'wb') as f:
        shutil.copyfileobj(file, f)

    current_user: Optional[Any] = get_current_user()
    user_id: Optional[str] = None if current_user is None else current_user.user_id

    info: dict = info if isinstance(info, dict) else {}
    info.setdefault('filename', filename)
    info.setdefault('filesize', os.path.getsize(blobfn))
    info.setdefault('timestamp', datetime.datetime.now().isoformat(timespec='seconds'))
    info.setdefault('user', user_id)

    with open(infofn, 'w') as f:
        json.dump(info, f, ensure_ascii=False)

    return new_file_id


def remove_file(entity: str, file_id: str) -> None:
    if not test_required(entity):
        raise exceptions.AccessDenied()

    if file_id.startswith('/'):
        # Not removing statically embedded files
        return

    file_id = uuid_from(file_id)
    root: str = get_file_root(entity, file_id)
    if not os.path.exists(root):
        return
    shutil.rmtree(root, ignore_errors=True)


def remove_files(entity: str, files_ids: List[str]) -> None:
    if not test_required(entity):
        raise exceptions.AccessDenied()

    for file_id in files_ids:
        file_id = uuid_from(file_id)
        if file_id.startswith('/'):
            # Not removing statically embedded files
            continue
        root: str = get_file_root(entity, file_id)
        if not os.path.exists(root):
            continue
        shutil.rmtree(root, ignore_errors=True)


async def get_embedded_file_response(
        file_id: str,
        request: Optional[Request] = None
) -> Union[FileResponse, NotModifiedResponse]:
    filepath: str = os.path.join(config.STATICS_ROOT, 'media', file_id.replace('..', ''))
    if not os.path.isfile(filepath):
        raise FileNotFoundError()

    filename: str = os.path.basename(filepath)
    disposition_raw: Union[str, bytes] = rfc6266.build_header(filename)
    disposition: str = disposition_raw.decode('latin-1') \
        if isinstance(disposition_raw, bytes) \
        else disposition_raw
    stat_result = await anyio.to_thread.run_sync(os.stat, filepath)

    response: FileResponse = FileResponse(
        filepath,
        headers={
            'Connection': 'keep-alive',
            'Content-Disposition': disposition,
        },
        stat_result=stat_result
    )

    if request is not None and file_not_modified(response.headers, request.headers):
        return NotModifiedResponse(response.headers)

    return response


async def get_file_response(
        entity: str,
        file_id: str,
        request: Optional[Request] = None
) -> Union[FileResponse, NotModifiedResponse]:
    if not test_readable(entity):
        raise exceptions.AccessDenied()

    if file_id.startswith('/'):
        # Just returning statically embedded file if the file_id
        # starts with leading slash.
        return await get_embedded_file_response(file_id, request)

    file_id = uuid_from(file_id)
    infofn: str = get_file_infofn(entity, file_id)

    with open(infofn, 'r') as f:
        info: dict = json.load(f)

    filename: str = info.get('filename', file_id)
    content_type: str = info.get('content_type', 'attachment')
    blobfn: str = get_file_blobfn(entity, file_id, filename)
    if not os.path.isfile(blobfn):
        raise FileNotFoundError()

    disposition_raw: Union[str, bytes] = rfc6266.build_header(filename)
    disposition: str = disposition_raw.decode('latin-1') \
        if isinstance(disposition_raw, bytes) \
        else disposition_raw

    stat_result = await anyio.to_thread.run_sync(os.stat, blobfn)

    response: FileResponse = FileResponse(
        blobfn,
        headers={
            'Connection': 'keep-alive',
            'Content-Disposition': disposition,
            'Content-Type': content_type
        },
        stat_result=stat_result
    )

    if request is not None and file_not_modified(response.headers, request.headers):
        return NotModifiedResponse(response.headers)

    return response


def get_abs_filename(entity: str, file_id: str) -> Optional[str]:
    if file_id.startswith('/'):
        filepath: str = os.path.join(config.STATICS_ROOT, 'media', file_id.replace('..', ''))
        if not os.path.isfile(filepath):
            return None
        return filepath

    file_id = uuid_from(file_id)
    infofn: str = get_file_infofn(entity, file_id)

    with open(infofn, 'r') as f:
        info: dict = json.load(f)

    filename: str = info.get('filename', file_id)
    blobfn: str = get_file_blobfn(entity, file_id, filename)
    if not os.path.isfile(blobfn):
        return None

    return blobfn

