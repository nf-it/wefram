"""
Provides some runtime contexts and functions.
"""

from typing import *
from collections import UserDict
from .requests import context as request_context
from . import cli


def start() -> None:
    """ The dummy function used in the startup. """
    pass


environment = {
    'execution_target': 'server'
}


class Context(UserDict):
    """
    The context class. Provides very important context-level functionality.
    The point is that almost every task, request and call rans in the context
    of the specific request or command-line session. So, two requests (for
    example, from two users or even from one browser, just two sequential
    requests from the one browser and tab) will have independent contexts, each
    with own set of data in it.

    The most useful context-level data are:

    * The database connection (both PostgreSQL & Redis);
    * The user's information which caused the request;
    * The session information;
    * The corresponding, applicable for the user localization info;
    etc.

    The example of using the context:

    .. highlight:: python
    .. code-block:: python

        from wefram.runtime import context
        from wefram.requests import route, Request, JSONResponse

        @route("/test", methods=['GET'])
        async def test_controller(request: Request) -> JSONResponse:
            # Lets return the current user's permissions. Just for example.
            return JSONResponse(context['permissions'])

    """

    def __init__(self):
        self.context = request_context
        super().__init__()

    @property
    def data(self):
        return self.context

    @data.setter
    def data(self, value):
        self.context.update(value)


context = Context()


async def within_cli(exe: Callable, *args, **kwargs) -> None:
    """ Executes the given function (exe) within CLI session, using declared special
    middlewares and plain, non-request-driven context

    :param exe:
        The executable *async* function to execute within CLI session
    :param args:
        Arguments (optional) whose about to be applied to the calling exe
    :param kwargs:
        Named arguments (optional) whose about to be applied to the calling exe
    """
    from . import run, middlewares

    run.ensure_started()
    context.context = {}  # Overriding the request-level context with usual dict

    cli_middlewares: list = middlewares.registered_cli
    call_stack: list = cli_middlewares + [cli.CliExecutable(exe, list(args), dict(kwargs))]

    if len(call_stack) == 1:  # if there are no CLI middlewares at all
        await exe()

    else:  # call `exe` within CLI middlewares
        await (call_stack[0](call_stack[1:])).call_next()
