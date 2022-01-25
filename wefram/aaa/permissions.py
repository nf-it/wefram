"""
Provides permissions defs (class), the registry of all registered in the project
permissions and the registration and operational functionality.
"""

from typing import *
from dataclasses import dataclass
from .. import logger, apps
from ..tools import CSTYLE, get_calling_app
from ..types.l10n import L10nStr


__all__ = [
    'Permission',
    'Permissions',
    'PermissionsItems',
    'PermissionsSet',
    'PermissionsSchema',
    'registered',
    'register',
    'get_permissions_set',
    'get_schema',
]


@dataclass
class Permission:
    """ A struct declaring the single permission used by one
    or the another application. Used in the registered permissions'
    registry on the platform level.
    """

    app: str
    name: str
    caption: str

    @property
    def key(self) -> str:
        return '.'.join([self.app, self.name])

    def __repr__(self) -> str:
        return self.key


Permissions = List[Permission]
PermissionsItems = List[dict]
PermissionsSet = Dict[str, Permissions]
PermissionsSchema = List[dict]


# Project's permissions registry
registered: Permissions = []


def register(
        name: str,
        caption: Union[str, L10nStr],
        app: Optional[str] = None
) -> Permission:
    """ Used by applications to register the permission in the system. This
    function registers the given permission with given unique name
    (application-wide) and with the given caption (which will be visible
    in the settings on the role administravie screen).
    As usual, if the calling application does not use the application
    name as the `app` param - the calling application name will be used to
    make the permission name unique across all enabled project applications.

    For example, application "mytest" calling this function:

    .. highlight:: python
    .. code-block:: python

        permissions.register('admin_access', "Administer everything")

    will register the permission 'mytest.admin_access' with caption
    "Administer everything" within the project and this permission will be
    accessible to be selected for the one or the another role, and the
    application will be able to restrict access to the different elements
    of it by using this permission by its name.

    :param name:
        The name of the permission
    :param caption:
        The visible to the roles administrators name of the permission
    :param app:
        Optional - the name of the app which this permission belongs to;
        if omitted - the calling application will be used as parent for
        the permission; otherwise - the specified application will be
        used as parent which gives the ability to extend an existing
        application with extra permissions.
    :return:
        The :class:`Permission` object
    """

    app_name: str
    if app is not None:
        app_name = app
    elif '.' in name:
        app_name, name = name.split('.', 2)
    else:
        app_name = get_calling_app()
    p = Permission(
        app=app_name,
        name=name,
        caption=caption
    )
    registered.append(p)
    logger.debug(f"registered permission {CSTYLE['red']}{p}{CSTYLE['clear']}")
    return p


def get_permissions_set() -> PermissionsSet:
    """ Returns a set of all registered in the project permissions, grouped
    by their parent applications. The resulting dict will look like:

    {
        'app1': [
            Permission(app='app1', name='permission1', caption="First one"),
            Permission(app='app1', name='permission2', caption="The second"),
            ...
        ],
        'app2: [
            ...
        ],
        ...
    }
    """

    res: PermissionsSet = {}
    for p in registered:
        res.setdefault(p.app, [])
        res[p.app].append(p)
    return res


def get_schema() -> PermissionsSchema:
    """ Returns the permission schema, which is useful for the administration
    representation, usually on the frontend side.
    """

    perms: PermissionsSet = get_permissions_set()
    schema: PermissionsSchema = []
    app_name: str
    app_permissions: Permissions
    for app_name, app_permissions in perms.items():
        permsset: dict = {
            'app': app_name,
            'caption': apps.get_app_caption(app_name),
            'permissions': [{
                'key': p.key,
                'caption': str(p.caption)
            } for p in sorted(app_permissions, key=lambda x: str(x.caption))]
        }
        schema.append(permsset)
    return sorted(schema, key=lambda x: str(x['caption']))

