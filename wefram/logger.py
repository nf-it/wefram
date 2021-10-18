"""
Used to log different messages to the stdout for the, mainly, debugging and
development purposes.
"""

from typing import *
from . import config
from .tools import CSTYLE, get_calling_app


__all__ = [
    'VERBOSE_LEVEL',
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'FATAL',
    'start',
    'set_level',
    'debug',
    'info',
    'warning',
    'error',
    'fatal'
]


VERBOSE_LEVEL: Dict[str, int] = {
    'fatal': 1,
    'error': 2,
    'warning': 3,
    'info': 4,
    'debug': 5
}
DEBUG: int = 5
INFO: int = 4
WARNING: int = 3
ERROR: int = 2
FATAL: int = 1
VERBOSE_STR: Dict[int, str] = {
    1: f"{CSTYLE['-red']}{'%-9s' % 'FATAL'}\033[0m{CSTYLE['clear']}",
    2: f"{CSTYLE['Red']}{'%-9s' % 'ERROR'}{CSTYLE['clear']}",
    3: f"{CSTYLE['Yellow']}{'%-9s' % 'WARNING'}{CSTYLE['clear']}",
    4: f"{CSTYLE['green']}{'%-9s' % 'info'}{CSTYLE['clear']}",
    5: f"{CSTYLE['white']}{'%-9s' % 'debug'}{CSTYLE['clear']}"
}
DEFAULT_VERBOSE_LEVEL: int = WARNING

if not isinstance(config.PRODUCTION, bool):
    raise TypeError('config.DEBUG must be (bool) type!')
if not isinstance(config.VERBOSE, (int, str, bool)):
    raise TypeError('config.VERBOSE must be (int, str, bool) type!')

VERBOSITY: int = VERBOSE_LEVEL['debug'] if not config.PRODUCTION else (
    config.VERBOSE if isinstance(config.VERBOSE, int) else (
        VERBOSE_LEVEL.get(config.VERBOSE, DEFAULT_VERBOSE_LEVEL) if isinstance(config.VERBOSE, str) else (
            INFO if config.VERBOSE else WARNING
        )
    )
)
if VERBOSITY is False:
    VERBOSITY = ERROR


def start() -> None:
    pass


def set_level(level: int) -> None:
    global VERBOSITY
    VERBOSITY = level


def _log(msg: str, level: int, clarification: Optional[str] = None):
    if level > VERBOSITY:
        return
    level_str = VERBOSE_STR.get(level, '').lower()
    clarification = '' if not clarification else f"{CSTYLE['red']}[{clarification}]{CSTYLE['clear']}"
    print(' '.join([
        s for s in [
            level_str,
            f"{CSTYLE['navy']}({get_calling_app()}){CSTYLE['clear']}",
            clarification,
            f"{CSTYLE['darker'] if level == DEBUG else ''}{msg}{CSTYLE['clear']}"
        ] if s
    ]))


def debug(msg: str, clarification: Optional[str] = None):
    _log(msg, DEBUG, clarification)


def info(msg: str, clarification: Optional[str] = None):
    _log(msg, INFO, clarification)


def warning(msg: str, clarification: Optional[str] = None):
    _log(msg, WARNING, clarification)


def error(msg: str, clarification: Optional[str] = None):
    _log(msg, ERROR, clarification)


def fatal(msg: str, clarification: Optional[str] = None):
    _log(msg, FATAL, clarification)

