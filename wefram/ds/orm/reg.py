"""
Provides the project's ORM schema registry functionality.
"""

from typing import *
import inspect
from ...tools import get_calling_app


__all__ = [
    'app_models',
    'models_by_name',
    'models_by_modulename',
    'models_by_tablename',
    'get_model',
    'tablename_of'
]


app_models = dict()
models_by_name = dict()
models_by_modulename = dict()
models_by_tablename = dict()


def get_model(name: str, app: str = None) -> Union[Any]:
    """
    Returns the model class by the corresponding model name and optional
    application name. If the ``app`` argument is omitted and the model
    does not includes the app name in its name (by using the complex name
    in the format <app>.<Class>) - the calling application will be used by
    default.
    """

    if name in models_by_tablename:
        return models_by_tablename[name]

    if '.' in name and name in models_by_modulename:
        return models_by_modulename[name]

    if '.' in name:
        app, name = name.split('.', 2)
    if not app:
        app = get_calling_app()

    if app in app_models and name in app_models[app]:
        return app_models[app][name]

    for app_name in app_models:
        if name not in app_models[app_name]:
            continue
        return app_models[app_name][name]

    return None


def tablename_of(model: Union[str, Any]) -> Optional[str]:
    """ Returns the name of the database table for the corresponding
    ORM model class. The tablename (usually) consists of the
    application name. followed by the model's class name. For example,
    for the applicaion "contacts" and model "Phones", the tablename
    will be ``contactsPhones``.

    :param model:
        If ``str`` type is provided - the corresponding model class
        will be found by :func:`~wefram.ds.get_model` function; otherwise
        the model class must be provided.

    :return:
        If the model class was not found (not been registered in the
        project) - ``None`` will be returned. Otherwise, the corresponding
        database table name will be returned.
    """

    from .model import DatabaseModel

    if isinstance(model, str):
        model: ClassVar = get_model(model)
        if model is None:
            return None
        return model.__tablename__
    elif inspect.isclass(model) and issubclass(model, DatabaseModel):
        return model.__tablename__
    raise ValueError("ds.tablename_of expects model to be given as (str) name or model class")
