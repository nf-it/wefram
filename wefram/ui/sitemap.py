"""
Provides a special case of sidebar layout - sitemap, which points to the
project's screens' structure.
"""

from typing import *
from ..types.l10n import L10nStr
from ..types.ui import BaseScreen
from . import sidebar


__all__ = [
    'folder',
    'append',
    'append_to',
    'register',
]


def _get_screen_url(screen: BaseScreen) -> Optional[str]:
    return screen.get_route_url()


def folder(
        name: str,
        caption: [str, L10nStr],
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[Union[str, Sequence[str]]] = None
) -> None:
    """ Appends the folder to the sidebar with given name (the name is
    very important because all childs about to be appended to the
    folder by its name).

    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    sidebar.folder(
        name=name,
        caption=caption,
        order=order,
        icon=icon,
        requires=requires
    )


def append(
        screen: BaseScreen,
        name: str,
        caption: [str, L10nStr],
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[Union[str, Sequence[str]]] = None
) -> None:
    """ Appends the given screen to the sitemap.

    :param screen: the screen which is about to be appended to the sitemap
    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    sidebar.append(
        name=name or screen.name,
        caption=caption or screen.caption or screen.name,
        order=order if order is not None else screen.order,
        icon=icon or screen.icon,
        requires=requires if requires is not None else screen.requires,
        url=_get_screen_url(screen),
        url_target='screen'
    )


def append_to(
        parent: str,
        screen: BaseScreen,
        name: str,
        caption: [str, L10nStr],
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[List[str]] = None
) -> None:
    """ Append the given screen to the sitemap within given folder. The folder have not
    to exist on the moment of the declaration.

    :param parent: the name of the sitemap folder item
    :param screen: the screen which is about to be appended to the sitemap
    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    sidebar.append_to(
        parent=parent,
        name=name,
        caption=caption,
        order=order,
        icon=icon,
        requires=requires,
        url=_get_screen_url(screen),
        url_target='screen'
    )


def register(screen: BaseScreen) -> BaseScreen:
    """ Decorator used to automate sitemap generation. Decorate the screen class
    with this decorator and the screen will automatically be added to the
    sitemap schema.
    """

    def decorator() -> BaseScreen:
        parent: Optional[str] = screen.parent
        if not parent:
            append(
                screen=screen,
                name=screen.name,
                caption=screen.caption or screen.name,
                order=screen.order,
                icon=screen.icon,
                requires=screen.requires
            )
        else:
            append_to(
                parent=parent,
                screen=screen,
                name=screen.name,
                caption=screen.caption or screen.name,
                order=screen.order,
                icon=screen.icon,
                requires=screen.requires
            )
        return screen
    return decorator()
