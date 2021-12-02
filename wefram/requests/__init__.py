from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette_context import context
from .routing import route, is_static_path, Route
from .responses import *
from . import routing, responses


def start() -> None:
    pass
