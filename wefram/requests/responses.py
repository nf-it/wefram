import typing
import os.path
from starlette.responses import (
    Response, HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse,
    FileResponse, JSONResponse as _starletteJSONResponse
)
from starlette.staticfiles import NotModifiedResponse
from starlette.background import BackgroundTask
from starlette.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from .. import config
from ..tools import json_encode, rerekey_snakecase_to_lowercamelcase


__all__ = [
    'Response',
    'NotModifiedResponse',
    'FileResponse',
    'HTMLResponse',
    'PlainTextResponse',
    'RedirectResponse',
    'StreamingResponse',
    'JSONResponse',
    'JSONedResponse',
    'StatusResponse',
    'NoContentResponse',
    'PrebuiltFile',
    'PrebuiltHTML',
    'templates'
]


templates = Jinja2Templates(directory=config.APPS_ROOT)


class JSONResponse(_starletteJSONResponse):
    def render(self, content: typing.Any) -> bytes:
        return json_encode(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class JSONedResponse(_starletteJSONResponse):
    def render(self, content: typing.Any) -> bytes:
        if isinstance(content, (dict, list, tuple)):
            content = rerekey_snakecase_to_lowercamelcase(content)
        return json_encode(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class StatusResponse(Response):
    def __init__(
            self,
            status_code: int = 200,
            content: typing.Any = None,
            headers: dict = None,
            media_type: str = None,
            background: BackgroundTask = None
    ):
        super().__init__(
            status_code=status_code,
            content=content,
            headers=headers,
            media_type=media_type,
            background=background
        )


class NoContentResponse(Response):
    def __init__(
            self,
            status_code: int = 204,
            headers: dict = None,
            media_type: str = None,
            background: BackgroundTask = None
    ):
        super().__init__(
            status_code=status_code,
            content=None,
            headers=headers,
            media_type=media_type,
            background=background
        )


class PrebuiltFile(FileResponse):
    def __init__(
            self,
            filename: str,
            status_code: int = 200,
            headers: dict = None,
            background: BackgroundTask = None
    ):
        fqfn: str = os.path.join(config.STATICS_ROOT, filename)
        if not os.path.isfile(fqfn):
            raise HTTPException(404, f"File not found: {filename}")
        super().__init__(
            fqfn,
            status_code=status_code,
            headers=headers,
            background=background
        )


class PrebuiltHTML(HTMLResponse):
    def __init__(
            self,
            filename: str,
            status_code: int = 200,
            headers: dict = None,
            background: BackgroundTask = None
    ):
        fqfn: str = os.path.join(config.STATICS_ROOT, filename)
        if not os.path.isfile(fqfn):
            raise FileNotFoundError(fqfn)
        with open(fqfn, 'r') as f:
            content = f.read()
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            background=background
        )
