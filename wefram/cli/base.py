"""
Provides the basic CLI (command-line interface) declarations.
"""

from typing import *
from dataclasses import dataclass
from abc import abstractmethod, ABC


__all__ = [
    'CliExecutable',
    'CliMiddleware'
]


@dataclass
class CliExecutable:
    func: Callable
    args: Optional[list]
    kwargs: Optional[dict]


class CliMiddleware(ABC):
    """
    The base middleware class used to create CLI middlewares. The ``__call__`` method
    MUST be defined. Example:

    .. highlight:: python
    .. code-block:: python

        from typing import *
        from wefram import cli

        class MyCliMiddleware(cli.CliMiddleware):
            async def __call__(self, call_next: Callable) -> None:
                # ... some python code prior to the next call
                # ...
                await self.call_next()
                # ...
                # ... some python code after the next call

    """

    def __init__(self, nextcalls):
        self._nextcalls: List[Union[Callable, CliExecutable]] = nextcalls

    async def call_next(self):
        def _makexec(_exe: CliExecutable):
            async def _f():
                await _exe.func(*_exe.args, **_exe.kwargs)
            return _f

        if len(self._nextcalls) > 1:
            next_middleware, other_nexts = self._nextcalls[0], self._nextcalls[1:]
            await self.__call__(next_middleware(other_nexts).call_next)
        elif isinstance(self._nextcalls[0], CliExecutable):
            exe: CliExecutable = self._nextcalls[0]
            await self.__call__(_makexec(exe))
        else:
            await self.__call__(self._nextcalls[0])

    @abstractmethod
    async def __call__(self, call_next: Callable) -> None:
        raise NotImplementedError

