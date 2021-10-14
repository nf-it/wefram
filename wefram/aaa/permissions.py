from typing import *
from dataclasses import dataclass
from .. import logger, apps
from ..tools import CSTYLE, get_calling_app
from ..types.l10n import L10nStr


__all__ = [
    'Permission',
    'TPermissions',
    'TPermissionsItems',
    'IPermissionsSet',
    'IPermissionsSchema',
    'registered',
    'register',
    'get_permissions_set',
    'get_schema',
]


@dataclass
class Permission:
    app: str
    name: str
    caption: str

    @property
    def key(self) -> str:
        return '.'.join([self.app, self.name])

    def __repr__(self) -> str:
        return self.key


TPermissions = List[Permission]
TPermissionsItems = List[dict]
IPermissionsSet = Dict[str, TPermissions]
IPermissionsSchema = List[dict]


registered: TPermissions = []


def register(
        name: str,
        caption: Union[str, L10nStr],
        app: Optional[str] = None
) -> Permission:
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


def get_permissions_set() -> IPermissionsSet:
    res: IPermissionsSet = {}
    for p in registered:
        res.setdefault(p.app, [])
        res[p.app].append(p)
    return res


def get_schema() -> IPermissionsSchema:
    perms: IPermissionsSet = get_permissions_set()
    schema: IPermissionsSchema = []
    app_name: str
    app_permissions: TPermissions
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


