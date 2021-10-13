from starlette.requests import Request
from starlette.routing import Route
from starlette.exceptions import HTTPException
from starlette_context import context
from .routing import route, is_static_path
from .responses import *
from .helpers import *
from . import routing, responses, helpers


def start() -> None:
    pass
