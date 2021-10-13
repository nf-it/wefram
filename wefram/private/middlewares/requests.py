from typing import *
import urllib.parse
from starlette.requests import Scope
from starlette.responses import PlainTextResponse, Response
from starlette_context.middleware import RawContextMiddleware as ContextMiddleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request, Headers
from ... import exceptions
from ...tools import rerekey_camelcase_to_snakecase


__all__ = [
    'RequestMiddleware',
    'ContextMiddleware',
]


class RequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        scope: Scope = request.scope
        headers: Headers = request.headers

        # Parsing URL query string
        query_string: str = scope['query_string'].decode('utf-8')
        parsed_query_args: Dict[str, List[str]] = urllib.parse.parse_qs(query_string)
        prepared_query_args: Dict[str, Union[str, List[str]]] = dict()
        for arg_name, arg_values in parsed_query_args.items():
            arg_name: str = str(arg_name)
            if arg_name.endswith('[]'):
                arg_name = arg_name[:-2]
                values: List[str] = [str(v) for v in arg_values if str(v) != '']
                if not values:
                    continue
                prepared_query_args[arg_name] = values
                continue
            value: str = str(arg_values[0])
            if value == '':
                continue
            prepared_query_args[arg_name] = value
        scope['query_args'] = prepared_query_args

        # Parsing request body (if possible)
        method: str = scope['method'].upper()
        payload: Optional[Any] = None
        payload_type: Optional[str] = None
        if method in ('POST', 'PUT') and 'content-type' in headers:
            content_type: str = headers['content-type'].lower()
            payload_type = 'plain'

            if 'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type:
                payload: Dict[str, Any] = {k: v for k, v in (await request.form()).items()}
                payload_type = 'form'

            elif 'application/json' in content_type:
                payload: [List, Dict] = await request.json()
                scope['payload_py'] = rerekey_camelcase_to_snakecase(payload)
                payload_type = 'json'

            else:
                payload: Any = await request.body()

        scope['payload'] = payload
        scope['payload_type'] = payload_type

        try:
            return await call_next(request)

        except exceptions.AccessDenied:
            return PlainTextResponse("Access denied", status_code=403)

        except exceptions.NotAuthenticated:
            return PlainTextResponse("Not authorized", status_code=401)
