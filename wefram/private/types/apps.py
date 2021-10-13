from typing import *
import types
import json
import os.path
from dataclasses import dataclass
from ...tools import app_root, json_from_file, json_to_file


__all__ = [
    'Manifest',
    'IAppsManifests',
    'IAppsModules',
    'IAppsMains'
]


@dataclass
class Manifest:
    name: str
    caption: str
    order: Optional[int]

    @classmethod
    def default_manifest(cls, name: str) -> 'Manifest':
        return cls(
            name=name,
            caption=name,
            order=None
        )

    @classmethod
    def manifest_for(cls, name: str) -> 'Manifest':
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
            order=data.get('order', None)
        )

    def write(self, filename: str) -> None:
        json_to_file({
            'name': self.name,
            'caption': self.caption,
            'order': self.order
        }, filename, indent=2)


IAppsModules = Dict[str, types.ModuleType]
IAppsMains = Dict[str, types.ModuleType]
IAppsManifests = Dict[str, Manifest]

