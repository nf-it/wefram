from typing import *
from ..requests import HTTPException, HTMLResponse, PrebuiltHTML
from ..tools import JSONexactValue
from .l10n import L10nStr


__all__ = [
    'BaseScreen'
]


class BaseScreen:
    _root_component: str
    _route_url: str
    _route_params: List[str]
    _requires: List[str]

    name: str
    app: str
    route: str = None
    component: Optional[str] = None
    caption: Optional[Union[str, L10nStr]] = None
    parent: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    requires: Optional[List[str]] = None
    params: Any = None

    def __init__(self):
        from ..aaa import permitted

        requires: List[str] = self._requires
        if requires and not permitted(requires):
            raise HTTPException(403)

    @classmethod
    async def endpoint(cls, *_) -> HTMLResponse:
        return PrebuiltHTML('index.html')

    @classmethod
    def _root_component_predef(cls) -> Optional[JSONexactValue]:
        if not cls._root_component:
            return None
        return JSONexactValue(
            f"React.lazy(() => import('{cls._root_component}'))"
        )

    @classmethod
    def schema_json(cls) -> dict:
        return {
            'name': cls.name,
            'rootComponentPath': cls._root_component,
            'rootComponent': cls._root_component_predef(),
            'requires': cls._requires,
            'routeUrl': cls.get_route_url(),
            'routeParams': cls._route_params,
            'params': cls.params or {}
        }

    @classmethod
    def runtime_json(cls) -> dict:
        return {
            'caption': str(cls.caption)
        }

    @classmethod
    def get_route_url(cls) -> str:
        return getattr(cls, '_route_url')
