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


def get_model(name: str, app_name: str = None) -> [None, ClassVar]:
    if name in models_by_tablename:
        return models_by_tablename[name]

    if '.' in name and name in models_by_modulename:
        return models_by_modulename[name]

    if '.' in name:
        app_name, name = name.split('.', 2)
    if not app_name:
        app_name = get_calling_app()

    if app_name in app_models and name in app_models[app_name]:
        return app_models[app_name][name]

    for app_name in app_models:
        if name not in app_models[app_name]:
            continue
        return app_models[app_name][name]

    return None


def tablename_of(model: [str, ClassVar]) -> (str, None):
    from .model import DatabaseModel

    if isinstance(model, str):
        model: ClassVar = get_model(model)
        if model is None:
            return None
        return model.__tablename__
    elif inspect.isclass(model) and issubclass(model, DatabaseModel):
        return model.__tablename__
    raise ValueError("ds.tablename_of expects model to be given as (str) name or model class")
