from typing import *
from collections import UserDict
from .requests import context as request_context
from . import cli


def start() -> None:
    pass


class Context(UserDict):
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

    :param exe: the executable *async* function to execute within CLI session
    :param args: arguments (optional) whose about to be applied to the calling exe
    :param kwargs: named arguments (optional) whose about to be applied to the
            calling exe
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
