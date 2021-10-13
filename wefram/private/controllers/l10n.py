from typing import *
import os.path
from ... import api
from ...requests import Request, PrebuiltFile, Response, JSONResponse, HTTPException
from ...runtime import context
from ...l10n.locales import Locale
from ...l10n.catalog import locate_dictionary_json
from ...l10n.config import BUILT_DICTS_PATH, BUILT_TEXTS_PATH


API_V1: int = 1


TextVariant = Literal['html', 'md', 'txt']


def get_text_by_id(
        location: str,
        text_id: str,
        variant: Optional[TextVariant] = None
) -> Tuple[str, TextVariant]:
    variants: List[str] = variant if variant else ['html', 'md', 'txt']
    variant: TextVariant
    for variant in variants:
        fn: str = os.path.join(location, f"{text_id}.{variant}")
        if not os.path.isfile(fn):
            continue
        with open(fn, 'r') as f:
            return f.read(), variant
    raise FileNotFoundError


@api.handle_get('/text/{app}/{text_id}', API_V1)
async def v1_get_text_by_id(request: Request) -> Response:
    app: str = str(request.path_params['app'])
    text_id: str = str(request.path_params['text_id'])
    variant: Optional[TextVariant] = request.scope['query_args'].get('variant', None)
    location: str = os.path.join(BUILT_TEXTS_PATH, app)
    if not os.path.isdir(location):
        raise HTTPException(404)
    text_msg: str
    text_variant: TextVariant
    try:
        text_msg, text_variant = get_text_by_id(location, text_id, variant)
    except FileNotFoundError:
        raise HTTPException(404)
    content_type: str = 'text/html' \
        if text_variant == 'html' \
        else ('text/markdown' if text_variant == 'md' else 'txt')
    return Response(text_msg, media_type=content_type)


@api.handle_get('/translated_text/{app}/{text_id}', API_V1)
async def v1_get_message_by_id(request: Request) -> Response:
    app: str = str(request.path_params['app'])
    text_id: str = str(request.path_params['text_id'])
    client_locale: Locale = context['locale']
    locales: List[str] = [str(client_locale), 'en']
    variant: Optional[TextVariant] = request.scope['query_args'].get('variant', None)
    for locale in locales:
        location: str = os.path.join(BUILT_DICTS_PATH, app, locale)
        if not os.path.isdir(location):
            continue
        text_msg: str
        text_variant: TextVariant
        try:
            text_msg, text_variant = get_text_by_id(location, text_id, variant)
        except FileNotFoundError:
            continue
        content_type: str = 'text/html' \
            if text_variant == 'html' \
            else ('text/markdown' if text_variant == 'md' else 'txt')
        return Response(text_msg, media_type=content_type)
    raise HTTPException(404)


@api.handle_get('/translations', API_V1)
async def v1_get_translations(request: Request) -> Response:
    locale: Locale = context['locale']
    filepath: str = locate_dictionary_json(locale)
    if not filepath:
        return JSONResponse({})
    if not os.path.exists(filepath):
        return JSONResponse({})
    return PrebuiltFile(filepath)

