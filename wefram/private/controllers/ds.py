from typing import *
from starlette.datastructures import FormData, UploadFile
from ... import api
from ...requests import (
    route,
    Request,
    JSONResponse,
    PlainTextResponse,
    NoContentResponse,
    FileResponse,
    HTTPException,
    NotModifiedResponse
)
from ...tools import array_from
from ...ds import storages


@api.handle_post('/storage/{entity}/file')
async def store_file(request: Request) -> PlainTextResponse:
    """ Store a single uploaded file to the storage, returning its
    FileId key.
    """
    entity: str = request.path_params['entity']
    payload: FormData = request.scope['payload']
    for data in payload.values():
        if not isinstance(data, UploadFile):
            continue
        data: UploadFile
        return PlainTextResponse(storages.upload_file_content(
            entity,
            data.file,
            data.filename,
            {
                'content_type': data.content_type
            }
        ))
    raise HTTPException(400)


@api.handle_post('/storage/{entity}/files')
async def store_files(request: Request) -> JSONResponse:
    """ Store several uploaded files to the storage, returning
    their FileIds as a list (array).
    """
    entity: str = request.path_params['entity']
    new_files_ids: List[str] = []
    payload: FormData = request.scope['payload']
    for data in payload.values():
        if not isinstance(data, UploadFile):
            continue
        data: UploadFile
        new_files_ids.append(storages.upload_file_content(
            entity,
            data.file,
            data.filename,
            {
                'content_type': data.content_type
            }
        ))
    return JSONResponse(new_files_ids)


@api.handle_put('/storage/{entity}/file/{file_id}')
async def replace_file(request: Request) -> PlainTextResponse:
    """ Replaces the previously stored (uploaded) file with the given
    new one, removing the old one.
    Not raising any error if there is no file with given UUID - acts
    like a just new file uploead in that case.
    """
    file_id: str = request.path_params['file_id']
    entity: str = request.path_params['entity']
    storages.remove_file(entity, file_id)

    payload: FormData = request.scope['payload']
    for data in payload.values():
        if not isinstance(data, UploadFile):
            continue
        data: UploadFile
        return PlainTextResponse(storages.upload_file_content(
            entity,
            data.file,
            data.filename,
            {
                'content_type': data.content_type
            }
        ))
    raise HTTPException(400)


@api.handle_delete('/storage/{entity}/file/{file_id}')
async def delete_file(request: Request) -> NoContentResponse:
    """ Deletes the existing stored file with the given UUID. """
    file_id: str = request.path_params['file_id']
    entity: str = request.path_params['entity']
    storages.remove_file(entity, file_id)
    return NoContentResponse()


@api.handle_delete('/storage/{entity}/files')
async def delete_files(request: Request) -> NoContentResponse:
    """ Deletes the existing stored files with the given UUIDs. """
    if 'fileId' not in request.scope['query_args']:
        raise HTTPException(400)
    file_ids: List[str] = array_from(request.scope['query_args']['fileId'])
    entity: str = request.path_params['entity']
    storages.remove_files(entity, file_ids)
    return NoContentResponse()


@api.handle_get('/storage/{entity}/file/{file_id}')
async def get_file(request: Request) -> FileResponse:
    file_id: str = request.path_params['file_id']
    entity: str = request.path_params['entity']
    try:
        return await storages.get_file_response(entity, file_id)
    except FileNotFoundError:
        raise HTTPException(404)


@route('//files/{entity}/{file_id}', methods=['GET'])
async def download(request: Request) -> Union[FileResponse, NotModifiedResponse]:
    file_id: str = request.path_params['file_id']
    entity: str = request.path_params['entity']
    try:
        return await storages.get_file_response(entity, file_id, request)
    except FileNotFoundError:
        raise HTTPException(404)

