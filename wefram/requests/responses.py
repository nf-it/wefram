"""
Provides different response types used in controllers. In addition to own type definitions
this module re-exports the Starlette defined types to make response handling one-placed.
"""

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
    'SuccessResponse',
    'PrebuiltFile',
    'PrebuiltHTML',
    'templates'
]


# Defines the Jinja2 template engine renderer.
templates = Jinja2Templates(directory=config.APPS_ROOT)


class JSONResponse(_starletteJSONResponse):
    """
    Redefines the Starlett's JSONReponse type with the Wefram one. This class
    overrides the ``render`` method, implementing the own JSONify logic by
    using extended :py:func:`~wefram.tools.json_encode` function which handles
    much more than the default one.
    """

    def render(self, content: typing.Any) -> bytes:
        return json_encode(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class JSONedResponse(_starletteJSONResponse):
    """
    The almost same as :py:class:`~wefram.requests.JSONResponse` response class,
    but in addition this class prepends the JSONifying with renaming given
    response content struct in the JSON-format names (renaming snakecase Pythonic
    names to lowerCamesCase JSONic ones). This happens if the ``dict``, ``list``
    or ``tuple`` being given as content.
    """

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
    """
    Simple response mainly to response with given HTTP status code, with
    optional text description.
    """

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
    """
    The simplification of the :py:class:`~wefram.requests.StatusResponse` by
    defaulting to 204 status code. This class do not support text
    description.
    """

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


class SuccessResponse(Response):
    """
    The simplification of the :py:class:`~wefram.requests.StatusResponse` by
    defaulting to 204 status code, with the text description as the first
    argument.
    """

    def __init__(
            self,
            text: str = None,
            status_code: int = None,
            headers: dict = None,
            media_type: str = None,
            background: BackgroundTask = None
    ):
        super().__init__(
            status_code=status_code if status_code is not None else (
                200 if text else 204
            ),
            content=text,
            headers=headers,
            media_type=media_type,
            background=background
        )


class PrebuiltFile(FileResponse):
    """
    Responses with a prubuilt (embedded in the assets) file content. The relative
    filename must be given, with application part in that path. The Starlette's
    ``FileResponse`` will be used to response the given file.

    :param filename:
        The relative to the statics root filename. This filename must include the
        application name in it too. For example:

        ``
        ...
        return PrebuiltFile('myapp/something/thefile.docx')
        ``

        As you can see - the statics root directory must not be included in the
        filename path.
    """

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
    """
    Responses with a prubuilt (embedded in the assets) HTML content. The relative
    filename must be given, with application part in that path. The Starlette's
    ``HTMLResponse`` will be used to response the given HTML file.

    :param filename:
        The relative to the statics root filename. This filename must include the
        application name in it too. For example:

        ``
        ...
        return PrebuiltFile('myapp/something/thefile.docx')
        ``

        As you can see - the statics root directory must not be included in the
        filename path.
    """

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
