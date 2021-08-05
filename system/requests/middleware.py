from typing import *
import urllib.parse
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request, Headers
from starlette.requests import HTTPConnection
from starlette.responses import PlainTextResponse, Response
from starlette_context.middleware import RawContextMiddleware as ContextMiddleware
from system import exceptions
import config


__all__ = [
    'RequestMiddleware',
    'ContextMiddleware',
]


class RequestMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive, send=send)
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
                payload_type = 'json'

            else:
                payload: Any = await request.body()

        scope['payload'] = payload
        scope['payload_type'] = payload_type

        try:
            await self.app(scope, receive, send)

        except exceptions.AccessDenied as exc:
            await PlainTextResponse("Access denied", status_code=403)(scope, receive, send)
            if not config.PRODUCTION:
                raise exc

        except exceptions.NotAuthenticated as exc:
            await PlainTextResponse("Not authorized", status_code=401)(scope, receive, send)
            if not config.PRODUCTION:
                raise exc
