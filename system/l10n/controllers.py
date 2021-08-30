import os.path
from .. import api
from ..requests import Request, PrebuiltFile, Response, JSONResponse
from ..runtime import context
from .locales import Locale
from .catalog import locate_dictionary_json


API_VER: int = 1


@api.handle_get('/translations', API_VER)
async def get_translations(request: Request) -> Response:
    locale: Locale = context['locale']
    filepath: str = locate_dictionary_json(locale)
    if not filepath:
        return JSONResponse({})
    if not os.path.exists(filepath):
        return JSONResponse({})
    return PrebuiltFile(filepath)
