""" A shortcut for executing make targets 'pip' and 'webpack' """

from . import pip, webpack


def run(*_) -> None:
    pip.run()
    webpack.run()

