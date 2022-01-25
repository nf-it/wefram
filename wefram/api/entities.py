"""
Provides the API entity functionalty.

The entity is a some class realizing CRUD (in general) functionality for
a general named entity (not matter what really happens in the class methods
on create, read, update & delete). The basic idea is to standardize the
CRUD with the same approach on different entities and applications, and
with standardized routing and paths.

This means that by declaring an entity class, the application programmer
automatically realizes standartized and HTTP-routed API methods for
interacting with it from the frontend of the project. In addition,
secutiry scopes checks (even on every CRUD method) automatically applies
to the given functionalty basing on declared requirements.

For example, the special case of the entity API is the ORM Model API which
gives understandable mechanics for read (SELECT from the database),
create (INSERT into database), update (UPDATE rows in database) and
delete (DELETE from the database) ORM-declared objects (rows).

But the target application may declare any logics on given methods. For
example, the entity may realize only read functionality, or make some
work with network communication, translating the request to the other
host, or something else.
"""

from typing import *
from abc import ABC, abstractmethod
from starlette.responses import Response
from .. import logger
from ..requests import routing, Route, Request
from ..requests.responses import (
    NoContentResponse,
    StatusResponse,
    JSONResponse,
    PlainTextResponse)
from ..tools import (
    CSTYLE,
    rerekey_camelcase_to_snakecase,
    int_or_none,
    get_calling_app,
    array_from,
    remove_from_array)
from .mixins import EntityAPIControllerRoute


__all__ = [
    'registered',
    'EntityCRUD',
    'EntityAPI',
    'register',
    'get_entity'
]


registered: Dict[str, Dict[str, 'EntityAPI']] = {}


class EntityCRUD(ABC):
    """
    Abstract class defining the entity CRUD logics to be implemented.
    """

    def __init__(self, key: Optional[Any] = None):
        self.key: Optional[Any] = key
        self.instance: Optional[Any] = None

    @staticmethod
    async def decode_value(key: str, s: Any) -> Any:
        """ Calls on every value (first-level, direct vision on the entity) fetched
        from the data source and before being resulted to the calling client. Used
        to decode packed value to the end-client format.
        """
        return s

    @staticmethod
    async def encode_value(key: str, s: Any) -> Any:
        """ Calls on every value (first-level, direct vision on the entity) given
        from the client and before being stored to the data source. Used to encode
        plain value to the format used to store this type or this exact value
        in the data storage.
        """
        return s

    @classmethod
    @abstractmethod
    async def create(cls, return_key: bool = False, **with_values) -> Any:
        """ The CRUD's CREATE operation, which must create a new entity object. """
        raise NotImplementedError

    @abstractmethod
    async def read(
            self,
            *keys: Union[str, int],
            count: bool = False,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            order: Optional[Union[str, List[str]]] = None,
            deep: bool = False,
            like: Optional[str] = None,
            ilike: Optional[str] = None,
            **filters: Any
    ) -> Any:
        """ The CRUD's READ operation, used both for listing of existing entity objects
        like a list, and fetching a single object details.
        """
        raise NotImplementedError

    @abstractmethod
    async def options(
            self,
            *keys: Union[str, int],
            like: Optional[str] = None,
            ilike: Optional[str] = None
    ) -> dict:
        """ About to return dict containing keys and corresponding human readable
        representations. For example, user's keys and corresponding names.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, *keys: Optional[Sequence[Union[str, int]]], **values) -> None:
        """ The CRUD's UPDATE operation, used to update the existing entity object (or
        objects, if the :param keys: can be handled by the real method).
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *keys: Optional[Sequence[Union[str, int]]]) -> None:
        """ The CRUD's DELETE operation, used to delete according entity object(s). """
        raise NotImplementedError


class EntityAPI(EntityCRUD, ABC):
    """
    The API-ready entity abstract class. Implements much of logics for the HTTP
    requests handling, endpointing to the EntityCRUD defined abstract methods.
    """

    app: str
    """ The application for which is entity is applicable to. Filled automatically
    at the entity registration time. """

    paths: dict
    """ The dict, containing registerd API paths for the every API method. For example:
    
    
    .. highlight:: python
    .. code-block:: python
     
        {
            'create': '/api/<app>/<EntityName>',
            'read': '/api/<app>/<EntityName>/<key>',
            'list': '/api/<app>/<EntityName>',
            'update': '/api/<app>/<EntityName>/<key>',
            'update_batch': '/api/<app>/<EntityName>',
            'options': '/api/<app>/<EntityName>',
            'options_resolve': '/api/<app>/<EntityName>/resolve',
            'delete': '/api/<app>/<EntityName>/<key>',
            'delete_batch': '/api/<app>/<EntityName>',
        }
    
    So, by accessing the entity class'es ``path`` property using the corresponding
    method key, the programmer may get the absolute URL for accessing the corresponding
    API method from the frontend.
    """

    name: Optional[str] = None
    """ The entity name. Filled automatically basing on the entity class name. """

    version: Optional[Union[str, int]] = None
    """ Optional, the API version. Gives an ability to handle different versions of the
    entity by declaring different entity classes (for example, basing on the one
    general class and hanlding differences between versions in the inheited ones. """

    path_prefix: Optional[str] = None
    """ Optional prefix used on the absolute routing path generation. This prefix, if
    specified, will be used in the routing path right after `/api` and before the rest
    of the path. For example:
    
    ``prefix = 'myprefix'``
    
    The path will be: ``/api/myprefix/myapp/v1/MyEntity``
    """

    path_suffix: Optional[str] = None
    """ Optional suffix used on the absolute routing path generation. This suffix, if
    specified, will be used in the routing path at the end. For example:
    
    ``suffix = 'mysuffix'``
    
    The path will be: ``/api/myapp/v1/MyEntity/mysuffix``
    """

    requires: Optional[Union[str, List[str]]] = None
    """ The general requirement for access rights. The programmer may list required
    permissions (scopes) here and them will be used by default for all API methods,
    except ones whose declares own requirements. 
    
    For example:
    
    .. highlight:: python
    .. code-block:: python
    
        class MyEntity(EntityAPI):
            requires = ['mypermission']
            
    """

    allow_create: Union[bool, List[str]] = True
    """ If set to `True` (default) - the method is allowed and will be routed. If
    **requires** property has been specified - it will be applied to this method.
    If set to `False` - the method is prohibited and will not be routed. If set
    to list type - then this method is allowed, will be routed, but requirements
    for security access permissions (scopes) will be overrided with the given
    list of permissions (even if has been specified by **requires** property).
    
    .. highlight:: python
    .. code-block:: python
    
        class MyEntity1(EntityAPI):
            # Permit the method, but require 'some_access' permission
            requires = ['some_access']
            allow_create = True  # may be omitted because by default is True
            
        class MyEntity2(EntityAPI):
            # Permit the method & requires 'other_permission', and not requires
            # any other permissions to access.
            requires = ['some_access']
            allow_create = ['other_permission']
    """

    allow_read: Union[bool, List[str]] = True
    """ If set to `True` (default) - the method is allowed and will be routed. If
        **requires** property has been specified - it will be applied to this method.
        If set to `False` - the method is prohibited and will not be routed. If set
        to list type - then this method is allowed, will be routed, but requirements
        for security access permissions (scopes) will be overrided with the given
        list of permissions (even if has been specified by **requires** property).

        .. highlight:: python
        .. code-block:: python

            class MyEntity1(EntityAPI):
                # Permit the method, but require 'some_access' permission
                requires = ['some_access']
                allow_read = True  # may be omitted because by default is True

            class MyEntity2(EntityAPI):
                # Permit the method & requires 'other_permission', and not requires
                # any other permissions to access.
                requires = ['some_access']
                allow_read = ['other_permission']
    """

    allow_options: Union[bool, List[str]] = True
    """ If set to `True` (default) - the method is allowed and will be routed. If
            **requires** property has been specified - it will be applied to this method.
            If set to `False` - the method is prohibited and will not be routed. If set
            to list type - then this method is allowed, will be routed, but requirements
            for security access permissions (scopes) will be overrided with the given
            list of permissions (even if has been specified by **requires** property).

            .. highlight:: python
            .. code-block:: python

                class MyEntity1(EntityAPI):
                    # Permit the method, but require 'some_access' permission
                    requires = ['some_access']
                    allow_options = True  # may be omitted because by default is True

                class MyEntity2(EntityAPI):
                    # Permit the method & requires 'other_permission', and not requires
                    # any other permissions to access.
                    requires = ['some_access']
                    allow_options = ['other_permission']
    """

    allow_update: Union[bool, List[str]] = True
    """ If set to `True` (default) - the method is allowed and will be routed. If
            **requires** property has been specified - it will be applied to this method.
            If set to `False` - the method is prohibited and will not be routed. If set
            to list type - then this method is allowed, will be routed, but requirements
            for security access permissions (scopes) will be overrided with the given
            list of permissions (even if has been specified by **requires** property).

            .. highlight:: python
            .. code-block:: python

                class MyEntity1(EntityAPI):
                    # Permit the method, but require 'some_access' permission
                    requires = ['some_access']
                    allow_update = True  # may be omitted because by default is True

                class MyEntity2(EntityAPI):
                    # Permit the method & requires 'other_permission', and not requires
                    # any other permissions to access.
                    requires = ['some_access']
                    allow_update = ['other_permission']
    """

    allow_delete: Union[bool, List[str]] = True
    """ If set to `True` (default) - the method is allowed and will be routed. If
            **requires** property has been specified - it will be applied to this method.
            If set to `False` - the method is prohibited and will not be routed. If set
            to list type - then this method is allowed, will be routed, but requirements
            for security access permissions (scopes) will be overrided with the given
            list of permissions (even if has been specified by **requires** property).

            .. highlight:: python
            .. code-block:: python

                class MyEntity1(EntityAPI):
                    # Permit the method, but require 'some_access' permission
                    requires = ['some_access']
                    allow_delete = True  # may be omitted because by default is True

                class MyEntity2(EntityAPI):
                    # Permit the method & requires 'other_permission', and not requires
                    # any other permissions to access.
                    requires = ['some_access']
                    allow_delete = ['other_permission']
    """

    @classmethod
    def path_base(cls) -> str:
        """ Internal method which returns a routing path base string basing (by default)
        on the entity class name. Useful for overriding how the entity sounds in the
        routing path (URL).
        """
        return cls.__name__

    @staticmethod
    def prepare_response(result: Any, status_code: int = 200) -> Response:
        """ Wrapper method which get the handler result and returns the HTTP response.
        This allows the handler methods (at CRUD model) to return Python-basic
        response like 'True' or dict or list, or even just a string, not dealing with
        HTTP response generation.

        :param result:
            The result of the API handler, which may be any kind of type.
        :param status_code:
            The status code which about to use as HTTP status code in the response;
            by default is '200 OK';
        :return:
            The formed and ready to send to the calling frontend client response.
        """

        # If the result is None - return 'No content' response.
        if result is None:
            return NoContentResponse()

        # If the result is boolean - return 'No content' success response
        # if it is true (204), or 400 error code otherwise (means something
        # gone wrong).
        elif result is True:
            return NoContentResponse()

        elif result is False:
            return StatusResponse(400)

        # Else, if there is a really plain response - like string or number,
        # then return a plain response.
        elif isinstance(result, (str, int, float)):
            return PlainTextResponse(str(result), status_code=status_code)

        # Else return JSONed response.
        return JSONResponse(result, status_code=status_code)

    @classmethod
    async def parse_request_payload(cls, request: Request) -> Optional[Dict[str, Any]]:
        """ Parses the payload of the request. If the payload is dict (most often case),
        then rename dict's keys from localCamesCase (typical for the JSON, JS & TS) to
        the snake_case (instead, typical for the Python).
        """

        payload: Optional[Any] = request.scope['payload']
        if not payload:
            return None
        if not isinstance(payload, dict):
            return payload
        return rerekey_camelcase_to_snakecase(payload)

    @classmethod
    def parse_request_arguments(cls, request: Request) -> Dict[str, str]:
        """ Parses the query arguments (if any) and returns them as dict. For the
        current moment - it is just a proxy function to the middleware prepared
        arguments' dict.
        """
        return request.scope['query_args']

    @classmethod
    async def handle_create(cls, request: Request) -> Response:
        """ Creates a single entity object, using JSON or FormData payload
        to set it up with the values. Returns no content response 201 if
        succeeded.

        If argument :argument return_key: setted to 'true' - return the new entity
        object's key (which requires FLUSH+COMMIT operation to be executed
        in the ORM prior to response been completed, usually).
        """
        with_values: Dict[str, Any] = (await cls.parse_request_payload(request)) or {}
        return cls.prepare_response(await cls.create(**with_values), 201)

    @classmethod
    async def handle_read(cls, request: Request) -> Response:
        """ The method both handling listing of entities, and returning a single
        entity data.
        If the :path_param key: is not None - the single entity object will be
        fetched and resulted as JSONed dict.
        If the :path_param key: is None - the list of entity objects will be
        fetched, corresponding with the given in args filters, and returned
        as JSONed list of objects' dicts.
        """
        args: Dict[str, str] = cls.parse_request_arguments(request)
        key: Optional[str] = request.path_params.get('key', None)
        entity: EntityAPI = cls(key)
        count: bool = str(args.pop('count', 'false')).lower() == 'true'
        offset: Optional[int] = int_or_none(args.pop('offset', None))
        limit: Optional[int] = int_or_none(args.pop('limit', None))
        order: Optional[str, List[str]] = args.pop('order', None)
        deep: Optional[bool] = str(args.pop('deep', 'false')).lower() == 'true' if 'deep' in args else None
        like: Optional[str] = args.pop('like', None)
        ilike: Optional[str] = args.pop('ilike', None)

        if args:
            args = rerekey_camelcase_to_snakecase(args)

        args = remove_from_array((
            'count',
            'offset',
            'limit',
            'order',
            'deep',
            'like',
            'ilike'
        ), args)

        return cls.prepare_response(await entity.read(
            count=count,
            offset=offset,
            limit=limit,
            order=order,
            deep=deep,
            like=like,
            ilike=ilike,
            **args
        ))

    @classmethod
    async def handle_options(cls, request: Request) -> Response:
        """ This method returns a dict, containing keys and corresponding
        object's human-readable representations, like names.
        """
        args: Dict[str, str] = cls.parse_request_arguments(request)
        keys: List[str] = args.get('keys', None) or []
        like: Optional[str] = args.pop('like', None)
        ilike: Optional[str] = args.pop('ilike', None)
        if request.method.upper() in ('POST', 'PUT'):
            payload: Optional[List[str]] = await cls.parse_request_payload(request)
            posted_keys: Optional[List[str]] = payload if isinstance(payload, list) else None
            if posted_keys:
                keys.extend(posted_keys)
        entity: EntityAPI = cls()

        return cls.prepare_response(await entity.options(*keys, like=like, ilike=ilike))

    @classmethod
    async def handle_update(cls, request: Request) -> Response:
        """ This method both can update a single entity object, given using
        :path_param key: argument (in the URL), and a set of entity objects,
        given by keys[] as URL argument (used for batch update of several
        objects at a time).
        """
        args: Dict[str, str] = cls.parse_request_arguments(request)
        key: Optional[str] = request.path_params.get('key', None)
        keys: List[str] = args.get('keys', None) or ([key] if key else [])
        entity: EntityAPI = cls(key)
        values: Dict[str, Any] = (await cls.parse_request_payload(request)) or {}
        return cls.prepare_response(await entity.update(*keys, **values))

    @classmethod
    async def handle_delete(cls, request: Request) -> Response:
        """ This method both can delete a single entity object, given using
        :path_param key: argument (in the URL), and a set of entity objects,
        given by keys[] as URL argument.
        """
        args: Dict[str, str] = cls.parse_request_arguments(request)
        key: Optional[str] = request.path_params.get('key')
        keys: List[str] = args.get('keys', None) or ([key] if key else [])
        entity: EntityAPI = cls(key)
        return cls.prepare_response(await entity.delete(*keys))


def register(cls: ClassVar[EntityAPI]) -> ClassVar[EntityAPI]:
    """ Decorator registers the EntityAPI-based class to handle entity based API logics. """

    from ..aaa import wrappers

    def _make_instanced_endpoint(_endpoint: Callable) -> Callable:
        async def _f(request: Request, *args, **kwargs):
            _instance = cls()
            return await _endpoint(cls, request, *args, **kwargs)
        return _f

    name: str = cls.name or cls.__name__

    cls: EntityAPI
    app_name: str = get_calling_app()
    path_base: str = cls.path_base()
    path_prefix: Optional[str] = cls.path_prefix or None
    path_suffix: Optional[str] = cls.path_suffix or None
    version: Optional[Union[str, int]] = cls.version or None
    requires: Optional[Union[str, List[str]]] = cls.requires
    allow_create: [bool, List[str]] = cls.allow_create
    allow_read: [bool, List[str]] = cls.allow_read
    allow_options: [bool, List[str]] = cls.allow_options
    allow_update: [bool, List[str]] = cls.allow_update
    allow_delete: [bool, List[str]] = cls.allow_delete
    all_cls_attrs: Dict[str, Any] = {
        k: getattr(cls, k) for k in dir(cls)
    }

    if version:
        version = f"v{version}"

    prefix: str = '/'.join([s for s in ['api', path_prefix] if s])
    paths: Dict[str, str] = {}

    def _suffix(_pre: Optional[str]) -> str:
        return '/'.join([s for s in [_pre, path_suffix] if s])

    def _permissions_by_app(_p: [str, Sequence[str]]) -> List[str]:
        return [(_x if '.' in _x else '.'.join([app_name, _x])) for _x in array_from(_p)]

    logger.debug(
        f"registered API entity {CSTYLE['red']}{app_name}.{name}{CSTYLE['clear']}"
    )

    controllers: List[EntityAPIControllerRoute] = [
        a for a in all_cls_attrs.values() if isinstance(a, EntityAPIControllerRoute)
    ]
    for ctrl in controllers:
        endpoint: Callable = _make_instanced_endpoint(ctrl.endpoint)
        if requires:
            endpoint = wrappers.requires(_permissions_by_app(requires))(endpoint)
        path = routing.format_path(path_base, prefix, version, _suffix(ctrl.path))
        routing.append(Route(path, endpoint, methods=ctrl.methods))

    # Routing the OPTIONS operation (used to return dict with keys
    # and representation)
    if allow_options:
        endpoint: Callable = cls.handle_options
        if isinstance(allow_options, (str, list, tuple, set)) or requires:
            required: List[str] = \
                array_from(allow_options) \
                if not isinstance(allow_options, bool) \
                else requires
            endpoint = wrappers.requires(_permissions_by_app(required))(endpoint)

        # Routing non-key path (fetches entities list)
        path = routing.format_path(path_base, prefix, version, path_suffix)
        paths['options'] = path
        routing.append(Route(path, endpoint, methods=['OPTIONS']))

        # Routing POST variant used for long key-based query
        path = routing.format_path(path_base, prefix, version, _suffix('resolve'))
        paths['options_resolve'] = path
        routing.append(Route(path, endpoint, methods=['POST']))

    # Routing the CREATE operation
    if allow_create:
        endpoint: Callable = cls.handle_create
        if isinstance(allow_create, (str, list, tuple, set)) or requires:
            required: List[str] = \
                array_from(allow_create) \
                if not isinstance(allow_create, bool) \
                else requires
            endpoint = wrappers.requires(_permissions_by_app(required))(endpoint)
        path = routing.format_path(path_base, prefix, version, path_suffix)
        paths['create'] = path
        routing.append(Route(path, endpoint, methods=['POST']))

    # Routing the READ operation
    if allow_read:
        endpoint: Callable = cls.handle_read
        if isinstance(allow_read, (str, list, tuple, set)) or requires:
            required: List[str] = \
                array_from(allow_read) \
                if not isinstance(allow_read, bool) \
                else requires
            endpoint = wrappers.requires(_permissions_by_app(required))(endpoint)

        # Routing non-key path (fethes entities list)
        path = routing.format_path(path_base, prefix, version, path_suffix)
        paths['list'] = path
        routing.append(Route(path, endpoint, methods=['GET']))

        # Routing keyed path (fetches entity detailed)
        path = routing.format_path(path_base, prefix, version, _suffix('{key}'))
        paths['read'] = path
        routing.append(Route(path, endpoint, methods=['GET']))

    # Routing the UPDATE operation
    if allow_update:
        endpoint: Callable = cls.handle_update
        if isinstance(allow_update, (str, list, tuple, set)) or requires:
            required: List[str] = \
                array_from(allow_update) \
                if not isinstance(allow_update, bool) \
                else requires
            endpoint = wrappers.requires(_permissions_by_app(required))(endpoint)

        # Routing non-key path
        path = routing.format_path(path_base, prefix, version, path_suffix)
        paths['update_batch'] = path
        routing.append(Route(path, endpoint, methods=['PUT']))

        # Routing keyed path
        # Both PUT and POST are accessible for UPDATE operation with the key,
        # because the CREATE operation uses POST withkey key specified.
        path = routing.format_path(path_base, prefix, version, _suffix('{key}'))
        paths['update'] = path
        routing.append(Route(path, endpoint, methods=['PUT', 'POST']))

    # Routing the DELETE operation
    if allow_delete:
        endpoint: Callable = cls.handle_delete
        if isinstance(allow_delete, (str, list, tuple, set)) or requires:
            required: List[str] = \
                array_from(allow_delete) \
                if not isinstance(allow_delete, bool) \
                else requires
            endpoint = wrappers.requires(_permissions_by_app(required))(endpoint)

        # Routing non-key path
        path = routing.format_path(path_base, prefix, version, path_suffix)
        paths['delete_batch'] = path
        routing.append(Route(path, endpoint, methods=['DELETE']))

        # Routing keyed path
        path = routing.format_path(path_base, prefix, version, _suffix('{key}'))
        paths['delete'] = path
        routing.append(Route(path, endpoint, methods=['DELETE']))

    # Storing the paths struct and ect
    setattr(cls, 'paths', paths)
    setattr(cls, 'app', app_name)

    # Registering the API entity
    registered.setdefault(app_name, {})[name] = cls

    return cls


def get_entity(name: str) -> Optional[EntityAPI]:
    """ Returns the entity by its given name. Returns None if the entity
    do not exist.
    """

    app_name: str
    entity_name: str
    if '.' not in name:
        app_name, entity_name = get_calling_app(), name
    else:
        app_name, entity_name = name.split('.', 1)
    if app_name not in registered:
        return None
    if entity_name not in registered[app_name]:
        return None
    return registered[app_name][entity_name]


