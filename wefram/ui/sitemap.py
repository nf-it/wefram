from typing import *
from dataclasses import dataclass
from ..aaa import permitted
from ..types.l10n import L10nStr
from ..types.ui import BaseScreen
from ..tools import CSTYLE, get_calling_app, array_from
from .. import logger


__all__ = [
    'append',
    'append_to',
    'register',
    'as_json',
]


_ORDER_INC: int = 100


@dataclass
class Item:
    """ A sitemap item class describing any item within project sitemap. """

    name: str
    caption: [str, L10nStr]
    screen: Optional[str]
    order: int
    icon: Optional[str]
    requires: Optional[List[str]] = None

    def __repr__(self):
        return f"sitemap.Item name={self.name} order={self.order} screen={self.screen}"

    @property
    def permitted(self) -> bool:
        if not self.requires:
            return True
        return permitted(self.requires)

    def as_json(self) -> dict:
        children: Optional[List[Item]] = _childrens.get(self.name, None)
        return {
            'name': self.name,
            'caption': self.caption,
            'screen': self.screen if children is None else None,
            'order': self.order,
            'icon': self.icon,
            'children': None if children is None else [
                x.as_json() for x in sorted(children, key=lambda y: y.order) if x.permitted
            ]
        }


_items: List[Item] = list()
_childrens: Dict[str, List[Item]] = dict()


def as_json() -> List[dict]:
    """ Returns dict ready to be JSONified as an answer to the web request. """

    return [
        x.as_json() for x in sorted(_items, key=lambda y: y.order) if x.permitted
    ]


def _make_requires(scopes: Optional[List[str]] = None) -> List[str]:
    if not scopes:
        return []
    return [
        (
            (scope if '.' in scope else '.'.join([get_calling_app(), scope]))
            if scope not in ('authenticated', 'guest')
            else scope
        )
        for scope in array_from(scopes)
    ]


def append(
        name: str,
        caption: [str, L10nStr],
        screen: Optional[str] = None,
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[Union[str, Sequence[str]]] = None
) -> None:
    """ Appends the given screen to the sitemap.
    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param screen: the endpoint screen name
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """
    if order is None:
        order = (len(_items) + 1) * _ORDER_INC
    _items.append(Item(
        name=name,
        caption=caption,
        screen=screen,
        order=order,
        icon=icon,
        requires=_make_requires(requires)
    ))
    # if icon:
    #     icons.require(icon)
    logger.debug(f"appended sitemap item: {CSTYLE['red']}{name}{CSTYLE['clear']}")


def append_to(
        parent: str,
        name: str,
        caption: [str, L10nStr],
        screen: str,
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[List[str]] = None
) -> None:
    """ Append the given screen to the sitemap within given folder. The folder have not
    to exist on the moment of the declaration.
    :param parent: the name of the sitemap folder item
    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param screen: the endpoint screen name
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    if order is None:
        order = (len(_childrens) + 1) * _ORDER_INC
    _childrens.setdefault(parent, list()).append(Item(
        name=name,
        caption=caption,
        screen=screen,
        order=order,
        icon=icon,
        requires=_make_requires(requires)
    ))
    logger.debug(f"appended child sitemap item: {CSTYLE['red']}{parent}/{name}{CSTYLE['clear']}")


def register(screen: BaseScreen) -> BaseScreen:
    """ Decorator used to automate sitemap generation. Decorate the screen class
    with this decorator and the screen will automatically be added to the
    sitemap schema.
    """

    def decorator() -> BaseScreen:
        parent: Optional[str] = screen.parent
        if not parent:
            append(
                name=screen.name,
                caption=screen.caption or screen.name,
                screen=screen.name,
                order=screen.order,
                icon=screen.icon,
                requires=screen.requires
            )
        else:
            append_to(
                parent=parent,
                name=screen.name,
                caption=screen.caption or screen.name,
                screen=screen.name,
                order=screen.order,
                icon=screen.icon,
                requires=screen.requires
            )
        return screen
    return decorator()
