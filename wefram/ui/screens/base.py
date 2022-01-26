"""
Provides the basic screens' classes available for inheritance with the real applications'
screens' classes. In addition, provides screens' management functionality like returning
the current screen schema and so on.
"""

from typing import *
import os.path
import re
from ...requests import routing, Request
from ...urls import asset_url
from ...tools import CSTYLE, get_calling_app, array_from, get_calling_module
from ...types.ui import BaseScreen
from ... import config, logger, ds, api, ui
from .types import RouteParams


class Screen(BaseScreen):
    """
    The basic, statically programmed at the frontend side of the application screen. None
    any extra actions from the backend is provided, except of on-demand loading of the
    JavaScript built code as .js file.
    """
    pass


class ManagedScreen(BaseScreen):
    """
    The backend controlled screen with very common definition on what is it. The basic
    point is that this screen will always fetch the result of its :meth:`~ManagedScreen.on_render`
    method on every screen open at the frontend, and pass the fetched results to the
    target screen container as ``managedProps`` struct. The format of this struct is not
    described and may be any JSONable, depending on what the screen container need to
    work with.

    The :meth:`~ManagedScreen.on_render` method calls on every screen open, produce and
    return the JSONable result, which responses to the frontend and about to be used by
    the managed screen at the frontend program code.

    The managed screen identifies by its name and the parent app where it was declated
    (or the one specified with the ``app`` property of the screen class).
    """

    screen_class = 'ManagedScreen'

    async def on_render(self) -> Any:
        """ Called on every screen open on the frontend side, returning some (really not
        defined here) data to the caller.
        """
        raise NotImplementedError


# -- DELAYED, has much more priorited tasks before this one
# class CompositeScreen(BaseScreen):
#     screen_class = 'CompositeScreen'
#
#     component: str = '/wefram/containers/CompositeScreen'
#     layout: Any = None
#     static: bool = None
#
#     @classmethod
#     def layout_schema(cls) -> CompositeLayout:
#         return []
#
#     @classmethod
#     def schema_json(cls) -> dict:
#         is_static: bool = cls.static is True or (cls.static is None and not callable(cls.layout))
#         layout: Optional[list] = None if not is_static else cls.layout_schema()
#
#         schema: dict = super().schema_json()
#         schema['params']['layout'] = layout
#         return schema
#
#     async def render(self, request: Request) -> Optional[CompositeLayout]:
#         raise NotImplementedError


class FilesScreen(BaseScreen):
    """
    The typo screen for managing and enumerating stored files. MUST be inherited
    by the end screen.

    For example:

    .. highlight:: python
    .. code-block:: python

        from wefram.ui import screens

        @register
        class MyFilesScreen(screens.FilesScreen):
            api_entity = 'some_storage'

    """

    component: str = '/wefram/containers/StoredFilesScreen'
    icon: str = asset_url('icons/files.png')

    api_entity: Any = None
    """ The corresponding registered storage entity of the file storage.
    Required to be set! """

    updatable: Union[bool, str, List[str]] = None
    """ Do allow files update (deletion, replacing, uploading)? Set to ``True`` to allow update
    for all users, ``False`` to decline update for everyone, or specify the permission scope
    (or scopes using ``list``) whose have permission to update. """

    @classmethod
    def schema_json(cls) -> dict:
        api_entity: Any = cls.api_entity
        if api_entity is None:
            raise ValueError(
                "FilesScreen.api_entity must be set to the corresponding API entity"
            )

        api_entity_name: str
        if isinstance(api_entity, type) and issubclass(api_entity, api.ModelAPI):
            api_entity_name = '.'.join([api_entity.app, api_entity.__name__])
        elif isinstance(api_entity, type) and issubclass(api_entity, ds.Model):
            meta: ds.Meta = getattr(api_entity, 'Meta')
            api_entity_name = '.'.join([meta.app_name, getattr(api_entity, '__decl_cls_name__')])
        else:
            api_entity_name = str(api_entity)

        api_entity = api.get_entity(api_entity_name)
        if api_entity is None:
            raise RuntimeError(
                f"API entity has not been registered: {api_entity_name}"
            )
        if not issubclass(api_entity, api.FilesModelAPI):
            raise RuntimeError(
                f"API entity is not FileModelAPI or ImageModelAPI entity type: {api_entity_name}"
            )

        schema: dict = super().schema_json()
        schema['params']['apiEntity'] = api_entity_name
        schema['params']['storageEntity'] = api_entity.storage_entity
        schema['params']['updatable'] = cls.updatable
        return schema


class ImagesScreen(FilesScreen):
    """
    The typo screen for managing and enumerating stored images. MUST be inherited
    by the application screen class.

    For example:

    .. highlight:: python
    .. code-block:: python

        from wefram.ui import screens

        @register
        class MyImagesScreen(screens.ImagesScreen):
            api_entity = 'some_storage'
            gap = 2
            row_height = 120
            columns = 4

    """

    component: str = '/wefram/containers/StoredImagesScreen'
    icon: str = asset_url('icons/images.png')

    columns: Optional[int] = None
    """ The quantity of columns per row of the gallery. """

    row_height: Optional[int] = None
    """ The height of each row of the gallery, in pixels. """

    gap: Optional[int] = None
    """ The gap (margin) between images in the gallery, in pixels. """

    @classmethod
    def schema_json(cls) -> dict:
        schema: dict = super().schema_json()
        if cls.columns:
            schema['params']['columns'] = int(cls.columns)
        if cls.row_height:
            schema['params']['rowHeight'] = int(cls.row_height)
        if cls.gap:
            schema['params']['gap'] = int(cls.gap)
        return schema


# The registry of all registered in the project screens.
registered: Dict[str, Any] = {}


def as_json() -> dict:
    """ Returns the screens' schema (for all defined on the backend screens) as ``dict``
    ready for JSONify. Used at the moment of ``make`` to generate the static TypeScript
    file defining all declared screens.
    """

    return {
        name: screen.schema_json() for name, screen in registered.items()
    }


def runtime_json() -> dict:
    """ Returns the screens' schema in the context of the client (especially useful
    for logged-in users).
    """

    return {
        name: screen.runtime_json() for name, screen in registered.items()
    }


def get_screen(name: str) -> ClassVar[BaseScreen]:
    """ Returns the screen class by its name. Returns ``None`` if there is no screen
    with given name been registered.
    """

    if name not in registered:
        return None
    return registered[name]


def get_screen_instance(name: str) -> Any:
    """ Returns the screen instance (the object of the screen class) by its name.
    Returns ``None`` if there is no screen with given name been registered.
    """

    screen_class = get_screen(name)
    if screen_class is None:
        return None

    return screen_class()


def register(
        _cls: ClassVar[BaseScreen] = None,
        sitemap: Optional[Union[bool, int, str, Tuple[str, int]]] = None
) -> ClassVar[BaseScreen]:
    """
    The decorator which registers the screen in the project.

    :param _cls:
    :param sitemap:
        if True - the screen will be registered at sitemap with class properties
        if [int] - the screen will be registered at sitemap with given order
        if [str] - the screen will be registered at sitemap within given folder
            by [str] folderid
        if (str, int) - the screen will be registered at sitemap within given
            folder (str) and with given order (int)
        otherwise screen will not be a part of sitemap
    """

    def _decorator(cls: ClassVar[BaseScreen]):
        name: str = cls.__name__

        def _make_requires(_scopes: Optional[List[str]]) -> List[str]:
            if not _scopes:
                return []
            return [
                (
                    (_scope if '.' in _scope else '.'.join([get_calling_app(), _scope]))
                    if _scope not in ('authenticated', 'guest')
                    else _scope
                )
                for _scope in array_from(_scopes)
            ]

        def _make_routeurl(_app: str, _route: str, _parent: Optional[str]) -> str:
            if _route.startswith('//'):
                return _route[1:]
            if _parent == _app:
                _parent = None
            return '/' + '/'.join([s.lower() for s in (
                _parent.strip() if isinstance(_parent, str) else '',
                _app.strip('/') if isinstance(_app, str) else '',
                _route.strip('/') if isinstance(_route, str) else ''
            ) if s])

        def _make_route(_path: Optional[str], _app: str, _parent: str) -> Tuple[str, RouteParams]:
            _path = _make_routeurl(_app, _path, _parent) \
                if _path \
                else _make_routeurl(_app, name, _parent)

            url: str = _path
            params: RouteParams = []
            extracted: List[str] = re.findall(r'{(.+?)}', _path)
            for p in extracted:
                n: str = p.split(':')[0]
                url = url.replace("{%s}" % p, f":{n}")
                params.append(n)
            return url, params

        def _make_routepath(_path: Optional[str], _app: str, _parent: str) -> str:
            return _make_routeurl(_app, _path, _parent) \
                if _path \
                else _make_routeurl(_app, name, _parent)

        def _make_root_component(_epath: Optional[str]) -> Optional[str]:
            app_module: str = get_calling_module()
            app_module_path: List[str] = app_module.split('.')
            path_prefix: str = app_module_path[0]
            if _epath:
                if _epath.startswith('/'):
                    return _epath[1:]
                if _epath.startswith('./'):
                    _epath = _epath[2:]
                    module_path: str = os.path.join(*app_module_path[:-1])
                    if os.path.isdir(os.path.join(config.PRJ_ROOT, module_path)):
                        return os.path.join(module_path, _epath)
                    return os.path.join(path_prefix, _epath[2:])
                return os.path.join(path_prefix, _epath)
            return None

        mro_ = cls.mro()
        if len(mro_) <= 3:
            return

        route_url: str
        route_params: RouteParams

        app_name: str = get_calling_app()
        screen_name: str = '_'.join([app_name, name])
        parent: Optional[str] = getattr(cls, 'parent', None)
        component: Optional[str] = getattr(cls, 'component', None)
        requires: Optional[List[str]] = getattr(cls, 'requires', None)
        route_url, route_params = _make_route(getattr(cls, 'route', None), app_name, parent)
        route_path: str = _make_routepath(getattr(cls, 'route', None), app_name, parent)

        root_component = _make_root_component(component)

        setattr(cls, '_root_component', root_component)
        setattr(cls, '_route_url', route_url)
        setattr(cls, '_route_params', route_params)
        setattr(cls, '_requires', _make_requires(requires))
        setattr(cls, 'app', app_name)
        setattr(cls, 'name', screen_name)

        if not root_component:
            raise TypeError(
                f"Screen.component not set for the native screen '{app_name}.{cls.__name__}'"
            )

        registered[screen_name] = cls
        logger.debug(f"registered screen {CSTYLE['green']}{screen_name}{CSTYLE['clear']}")

        endpoint: Callable = getattr(cls, 'endpoint')
        routing.append(routing.Route(route_path, endpoint, methods=['GET']))

        # Handling sitemap registration, if needed.
        if sitemap is not None and sitemap is not False:
            sitemap_parent: Optional[str] = sitemap if isinstance(sitemap, str) else (
                sitemap[0]
                if isinstance(sitemap, (tuple, list)) and len(sitemap) == 2 and isinstance(sitemap[0], str)
                else cls.parent
            )
            order: Optional[int] = sitemap if isinstance(sitemap, int) else (
                sitemap[1]
                if isinstance(sitemap, (tuple, list)) and len(sitemap) == 2 and isinstance(sitemap[1], int)
                else cls.order
            )
            if not sitemap_parent:
                ui.sitemap.append(
                    screen=cls,
                    name=cls.name,
                    caption=cls.caption or cls.name,
                    order=order,
                    icon=cls.icon,
                    requires=cls.requires
                )
            else:
                ui.sitemap.append_to(
                    parent=sitemap_parent,
                    screen=cls,
                    name=cls.name,
                    caption=cls.caption or cls.name,
                    order=order,
                    icon=cls.icon,
                    requires=cls.requires
                )

        return cls

    if _cls is not None:
        return _decorator(_cls)

    return _decorator

