""" A shortcut for make targets for full frontend generation """

from typing import *
from . import assets, screens, react


def run(roots: List[str]) -> None:
    assets.run(roots)
    screens.run()
    react.run()
