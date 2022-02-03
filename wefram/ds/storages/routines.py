"""
Provides general purpose functions for working with storage entities and stored
(uploaded) files.
"""

from typing import *
from uuid import uuid4
import os
import json
import shutil
import datetime
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
    """ Returns ``True`` if the given requested file was not modified, to realise the
    'Not modified' HTTP answer to better traffic economy and better browser (client-side)
    file cache usage.
    """

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
    """ Returns ``True`` if the current user has access to modify file storage,
    meaning upload, replace or delete operation.
    """

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
    """ Returns ``True`` if the current user is allowed to read files from the storage
    entity, by downloading them.
    """

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
    """ Returns the absolute path to the file location, but without the
    corresponding filename.
    """

    return os.path.join(config.FILES_ROOT, entity, file_id[:2])


def get_file_blobfn(entity: str, file_id: str, filename: str) -> str:
    """ Returns the absolute path to the file's content struct by its storage
    entity name and corresponding ``file_id``.
    """

    dir1, dir2, dir3 = get_file_subpath(file_id)
    return os.path.join(config.FILES_ROOT, entity, dir1, dir2, dir3, filename)


def get_file_infofn(entity: str, file_id: str) -> str:
    """ Returns the absolute path to the file's info struct by its storage
    entity name and corresponding ``file_id``.
    The filename will be the same as content-filename with '.fileinfo.json'
    suffix appended.
    """

    dir1, dir2, dir3 = get_file_subpath(file_id)
    return os.path.join(config.FILES_ROOT, entity, dir1, dir2, dir3, '.fileinfo.json')


def upload_file_content(
        entity: str,
        file: Any,
        filename: str,
        info: Optional[dict] = None,
        force_id: Optional[str] = None
) -> str:
    """ Stores the given file in the file system of the server within given storage
    entity. There are two files will be created: the file with the real content and
    the file with information struct, next to the content one.

    :param entity:
        The corresponding storage entity. The full entity name must be used, including
        parent application name. For example: ``myapp.my_storage``.

    :param file:
        The file object itself.

    :param filename:
        The filename of the file. It is not included in the ``file`` object, so must
        be specified here.

    :param info:
        The optional ``dict`` of extra parameters or information which about to be
        stored in the corresponding file info struct.

    :param force_id:
        The optional argument which provides the ability of force the ``file_id``
        instead of generation the new one. Useful for replacing the file, keeping
        the old ``file_id``.

    :return:
        The new file id (or the ``force_id`` value, if have been specified).

    :raises:
        The `AccessDenied` if the current user has no access.
    """

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
    """ Removes the file from the file system of the server.

    :param entity:
        The corresponding storage entity. The full entity name must be used, including
        parent application name. For example: ``myapp.my_storage``.

    :param file_id:
        The corresponding ``file_id`` of the file to remove.

    :raises:
        The `AccessDenied` if the current user has no access.
    """

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
    """ Removes files from the file system of the server.

    :param entity:
        The corresponding storage entity. The full entity name must be used, including
        parent application name. For example: ``myapp.my_storage``.

    :param files_ids:
        The list of corresponding ``file_id`` of files to remove.

    :raises:
        The `AccessDenied` if the current user has no access.
    """

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
    """ The special case of the file response which returns the embedded in the
    project file. The embedded file is not the one uploaded, but instead - is the
    file which was placed in the assets of one or the another application. For
    example, if the application put the default icon image to the assets (or even
    not modificable file) - this file will be named embedded in this scenario.

    The embedded ``file_id`` always starts with the leading slash symbol (``/``)
    and the corresponding relative path to the file. The path must include both
    parent application and the rest of the path.

    The described above path may be created with helper function, see
    :py:func:`wefram.urls.asset_url` for detailts.

    For example: `/my_very_app/images/my_icon.png`

    :param file_id:
        The ``file_id`` of the corresponding file - the relative asset path.

    :param request:
        The ``Request`` object of the request.

    :return:
        ``NotModifiedResponse`` if, basing on the request, the requested file
        was not modified, or the ``FileResponse`` instead.

    :raises:
        ``FileNotFound`` exception if the given file is not exists.
    """

    filepath: str = os.path.join(config.STATICS_ROOT, 'assets', file_id.replace('..', ''))
    if not os.path.isfile(filepath):
        raise FileNotFoundError()

    filename: str = os.path.basename(filepath)
    # RFC-6266 is required here, but the corresponding package is BROKEN
    # TODO!
    # disposition_raw: Union[str, bytes] = rfc6266.build_header(filename)
    # disposition: str = disposition_raw.decode('latin-1') \
    #     if isinstance(disposition_raw, bytes) \
    #     else disposition_raw
    stat_result = await anyio.to_thread.run_sync(os.stat, filepath)

    response: FileResponse = FileResponse(
        filepath,
        headers={
            'Connection': 'keep-alive',
            # 'Content-Disposition': disposition,  # TODO
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
    """
    Generates the file response for the given storage ``entity`` and corresponding ``file_id``,
    and with usage of the given ``request``. If the requesting client (usually web browser)
    supports caching of files and provides the neccessary data in the request - the
    ``NotModifiedResponse`` may be returned instead of the real file if the requested file was
    not modified and the cached file on the client side is still valid.

    If the given ``file_id`` starts with a leading slash symbol - :py:func:`get_embedded_file_response`
    function will be used instead to return embedded file.

    :param entity:
        The fully qualified storage entity, including parent application name. For example:
        `myapp.my_file_storage`.

    :param file_id:
        The corresponding file id.

    :param request:
        The ``Request`` object of the request.

    :return:
        ``NotModifiedResponse`` if, basing on the request, the requested file
        was not modified, or the ``FileResponse`` instead.

    :raises:
        ``FileNotFound`` exception if the given file is not exists.

    :raises:
        ``AccessDenied`` exception if the user (from the request context) has no access
        to the file.
    """

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

    # TODO
    # disposition_raw: Union[str, bytes] = rfc6266.build_header(filename)
    # disposition: str = disposition_raw.decode('latin-1') \
    #     if isinstance(disposition_raw, bytes) \
    #     else disposition_raw

    stat_result = await anyio.to_thread.run_sync(os.stat, blobfn)

    response: FileResponse = FileResponse(
        blobfn,
        headers={
            'Connection': 'keep-alive',
            # 'Content-Disposition': disposition,  # TODO
            'Content-Type': content_type
        },
        stat_result=stat_result
    )

    if request is not None and file_not_modified(response.headers, request.headers):
        return NotModifiedResponse(response.headers)

    return response


def get_abs_filename(entity: str, file_id: str) -> Optional[str]:
    """ Returns the absolute filename of the corresponding, uploaded file. If the file
    is not exists - returns ``None`` instead.

    Note that if the ``file_id`` starts with slash (``/`` symbol), then the ``file_id`` will
    be interpreted as static file path and will be rooted to the static files root directory,
    in the 'assets' folder. This makes possible to statically place files and specify their
    file_ids in the database (for example, default files whose about to be used if there are
    not uploaded ones).
    """

    if file_id.startswith('/'):
        filepath: str = os.path.join(config.STATICS_ROOT, 'assets', file_id.replace('..', ''))
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

