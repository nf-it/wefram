"""
Provides the project's sidebar layout definition and registry.
"""

from typing import *
from dataclasses import dataclass
from ..aaa import permitted
from ..types.l10n import L10nStr
from ..tools import CSTYLE, get_calling_app, array_from
from .. import logger


__all__ = [
    'folder',
    'append',
    'append_to',
    'as_json',
]


_ORDER_INC: int = 100


@dataclass
class Item:
    """
    A sidebar item class describing any item within project sidebar.
    """

    name: str
    """ The item's system name. """

    caption: [str, L10nStr]
    """ The item's human readable, rendered caption. """

    url: Optional[str]
    """ The target on-click URL. If set, the item will be rendered inside the
    link <A> element with given target URL. """

    url_target: Optional[Literal['screen', 'blank', 'redirect', 'container']]
    """ The target for the item link. Possible values are:
    
    * 'screen' - the target URL is a screen and the internal SPA routing will be used;
    * 'blank' - the target URL must be opened in the new tab;
    * 'redirect' - the target URL must be opened in the same tab;
    * 'container' - the internal option telling the renderer that this is a folder item; 
    """

    endpoint: Optional[str]
    """ Reserved for the future use. """

    order: int
    """ The order decribing the placement of this item among other ones. The higher
    values places the item lower, while lower values - upper. """

    icon: Optional[str]
    """ The relative path to the item's icon file. """

    requires: Optional[List[str]] = None
    """ A list of required permission scopes. If the current user has no required
    scopes - the item will not be rendered for him|her. """

    def __repr__(self):
        return f"sidebar.Item name={self.name} order={self.order}"

    @property
    def permitted(self) -> bool:
        """ Returns ``True`` if the current user is able to see this item. """

        if not self.requires:
            return True
        return permitted(self.requires)

    def as_json(self) -> dict:
        """ Returns the item JSON-ready dict for responsing to the client side. """

        children: Optional[List[Item]] = _childrens.get(self.name, None)
        return {
            'name': self.name,
            'caption': self.caption,
            'url': self.url if children is None else None,
            'urlTarget': self.url_target if children is None else None,
            'endpoint': self.endpoint if children is None else None,
            'order': self.order,
            'icon': self.icon,
            'children': None if children is None else [
                x.as_json() for x in sorted(children, key=lambda y: y.order) if x.permitted
            ]
        }


_items: List[Item] = list()
_containers: Dict[str, Item] = dict()
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


def folder(
        name: str,
        caption: [str, L10nStr],
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[Union[str, Sequence[str]]] = None
) -> None:
    """ Appends the folder to the sidebar with given name (the name is
    very important because all childs about to be appended to the
    folder by it's name).

    :param name: the name of the sitemap item
    :param caption: the caption which will be displayed to the end user
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    if not name:
        raise ValueError("`name` is required for the sitebar folder!")

    if name in _containers:
        raise KeyError(f"sidebar folder with name {name} is already exists!")

    if order is None:
        order = (len(_items) + 1) * _ORDER_INC
    item: Item = Item(
        name=name,
        caption=caption,
        order=order,
        icon=icon,
        requires=_make_requires(requires),
        url=None,
        url_target='container',
        endpoint=None
    )
    _items.append(item)
    _containers[name] = item
    logger.debug(f"appended sidebar folder: {CSTYLE['red']}{name}{CSTYLE['clear']}")


def append(
        name: str,
        caption: [str, L10nStr],
        url: Optional[str] = None,
        url_target: Optional[Literal['screen', 'blank', 'redirect']] = None,
        endpoint: Optional[str] = None,
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[Union[str, Sequence[str]]] = None
) -> None:
    """ Appends the given screen to the sidebar.
    :param name: the name of the sidebar item
    :param caption: the caption which will be displayed to the end user
    :param url: the URL of the destination for the given sidebar item
    :param url_target: the target how to open the given :param url: - possible options are
        * 'screen' (open as screen within the loaded frontend),
        * 'blank' (open at the new tab of the browser),
        * 'redirect' (open by plain redirecting the current URL to the new one, leaving the frontend)
    :param endpoint: reserved for the future use - the name of the registered endpoint which
        to execute on the item click;
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """
    if order is None:
        order = (len(_items) + 1) * _ORDER_INC
    _items.append(Item(
        name=name,
        caption=caption,
        url=url,
        url_target=url_target,
        endpoint=endpoint,
        order=order,
        icon=icon,
        requires=_make_requires(requires)
    ))
    logger.debug(f"appended sidebar item: {CSTYLE['red']}{name}{CSTYLE['clear']}")


def append_to(
        parent: str,
        name: str,
        caption: [str, L10nStr],
        url: Optional[str] = None,
        url_target: Optional[Literal['screen', 'blank', 'redirect']] = None,
        endpoint: Optional[str] = None,
        order: Optional[int] = None,
        icon: Optional[str] = None,
        requires: Optional[List[str]] = None
) -> None:
    """ Append the given screen to the sidebar within given folder. The folder have not
    to exist on the moment of the declaration.
    :param parent: the name of the sidebar folder item
    :param name: the name of the sidebar item
    :param caption: the caption which will be displayed to the end user
    :param url: the URL of the destination for the given sidebar item
    :param url_target: the target how to open the given :param url: - possible options are
        * 'screen' (open as screen within the loaded frontend),
        * 'blank' (open at the new tab of the browser),
        * 'redirect' (open by plain redirecting the current URL to the new one, leaving the frontend)
    :param endpoint: reserved for the future use - the name of the registered endpoint which
        to execute on the item click;
    :param order: numerical order towards to the other items in the same corresponding folder
    :param icon: the icon name
    :param requires: array of permission scopes required to display this item
    """

    if order is None:
        order = (len(_childrens) + 1) * _ORDER_INC
    _childrens.setdefault(parent, list()).append(Item(
        name=name,
        caption=caption,
        url=url,
        url_target=url_target,
        endpoint=endpoint,
        order=order,
        icon=icon,
        requires=_make_requires(requires)
    ))
    logger.debug(f"appended child sidebar item: {CSTYLE['red']}{parent}/{name}{CSTYLE['clear']}")

