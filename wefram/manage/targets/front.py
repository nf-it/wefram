""" A shortcut for make targets for full frontend generation """

from typing import *
from . import assets, prefront, react


def run(roots: List[str]) -> None:
    assets.run(roots)
    prefront.run()
    react.run()
