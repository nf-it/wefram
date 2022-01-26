"""
Provides types definitions for applications management and runtime usage.
"""

from typing import *
from types import ModuleType
import os.path
from dataclasses import dataclass
from ..tools import app_root, json_from_file, json_to_file


__all__ = [
    'Manifest',
    'IAppsManifests',
    'IAppsModules',
    'IAppsMains'
]


@dataclass
class Manifest:
    """ The application manifest dataclass. """

    name: str
    """ The application system name. """

    caption: str
    """ The application human readable and displayable name. """

    order: Optional[int]
    """ The order in which this application will be handled and rendered in the enumerations. """

    requirements: dict
    """ The structure of third-party Python (backend) and TypeScript (frontend) packages'
    dependencies. This struct, if declared, must be formed as dict:
    
    ``
    {
        ...
        "requirements": {
            "pip": {
                "<package_name>": "<compatible_version>",
                "starlette": "latest",
                "SQLAlchemy": "1.4",
                ...
            },
            "node": {
                "<packageName>": "<compatibleVersion>",
                "@mui/system": "^5.0.6",
                "@mui/lab": "==5.0.0-alpha.53",
                "sass-loader": "latest",
                ...
            }
        },
        ... 
    }
    ``
    """

    @classmethod
    def default_manifest(cls, name: str) -> 'Manifest':
        """ Returns the default manifest by the application name. """

        return cls(
            name=name,
            caption=name,
            order=None,
            requirements={}
        )

    @classmethod
    def manifest_for(cls, name: str) -> 'Manifest':
        """ Returns the manifest dataclass for the given by ``name`` application. """

        root: Optional[str] = app_root(name)
        if not root:
            return cls.default_manifest(name)
        filename: str = os.path.join(root, 'manifest.json')
        if not os.path.isfile(filename):
            return cls.default_manifest(name)
        data: dict = json_from_file(filename)
        if not isinstance(data, dict):
            raise TypeError(f"invalid app manifest (is not dict) for `{name}`")
        return cls(
            name=name,
            caption=data.get('caption', name),
            order=data.get('order', None),
            requirements=data.get('requirements', None) or {}
        )

    def write(self, filename: str) -> None:
        """ Write the manifest dataclass to the given ``filename``. """

        json_to_file({
            'name': self.name,
            'caption': self.caption,
            'order': self.order,
            'requirements': self.requirements
        }, filename, indent=2)


IAppsModules = Dict[str, ModuleType]
IAppsMains = Dict[str, ModuleType]
IAppsManifests = Dict[str, Manifest]

