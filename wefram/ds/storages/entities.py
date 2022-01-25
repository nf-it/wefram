"""
Provides the file storages functionality, defining the **storage entity** term.

While most projects based on the Wefram platform (strictly speaking, almost all
projects basing on anything) stores data in the database, some amount of data
about to be stored in the file system of the server (or servers). Of cource, we
are speaking about uploading files to the server.

The Wefram provides the special way of storing uploaded files. First of all, it
stores NOT in the PostgreSQL database. Instead, Wefram saves uploaded files to
the file system of the server (not matter is that file system a local one or
is mounted network storage).

To control the file storing, especially across different applications and
different files purposes, Wefram introduces the **storage entity** term.

The entity, strictly speaking, is a directory, dedicated to the specific
application (always to the one or the another app) and to the specific
purpose.

This means that all application will always have own file storages, and there
will never be conflict between them. In addition, each application may have
more than one file storage, dividing the storage into separate purposes.

For example, we have the example application *Services*. Let's say that each
service has an icon, which can be managed (uploaded, replaced). This means
that the application 'Service' needs a file storage. Now, let's say that the
application, in addition, has the SSR rendered page for clients, describing
whose services the abstract firm is providing. And let's say that there are
several photos uses on that page. So, we need the another file storage which
will be used to store those photos, with ability to replace them with the
another ones or even upload more or less.

Let's show an example how to declare those two example storages:

.. highlight:: python
.. code-block:: python

    # file: services/app.py  [services.app]

    from wefram import ds

    ds.storages.register(name='icons')
    ds.storages.register(name='album')


Now, let's use those entities for example. To show the usage of them we
will take some other Wefram logics in deal, from the [ds] module.

.. highlight:: python
.. code-block:: python

    # file: services/models.py  [services.models]

    from wefram import ds

    # Declaring the Service ORM model with uploadable image within it
    class Service(ds.Model):
        id = ds.UuidPrimaryKey()
        name = ds.Column(ds.Caption(), nullable=False, default='')
        icon = ds.Image('services.icons')
        # here we specified ``<app>.<storage>`` form of the storage entity, but
        # if the entity is owned by the same app, as calling one - app name may be
        # omitted.

    # Declaring the album model used to store several images
    ServiceAlbum = ds.images_model(
        name='ServiceAlbum',
        entity='services.album'
    )

"""

from typing import *
from dataclasses import dataclass
from ...tools import CSTYLE, get_calling_app
from ... import logger


__all__ = [
    'StorageEntity',
    'registered',
    'register'
]


@dataclass
class StorageEntity:
    app: str
    name: str
    requires: Optional[List[str]]
    readable: Optional[List[str]]


# The registry of all project declared storage entities. The format
# of app.entity->EntityObject is used:
# {
#   "myapp1.icons": StorageEntity(name='myapp1.icons'),
#   "myapp1.album": StorageEntity(name='myapp1.album')
# }
registered: Dict[str, StorageEntity] = {}


def register(
        name: str,
        requires: Optional[List[str]] = None,
        readable: Optional[List[str]] = None,
        app: Optional[str] = None
) -> None:
    """ Used to register the storage entity in the project for the application.

    :param name:
        The name of the storage entity. Must be unique in the application context. It may be
        the same as other entity in the other application - this will not cause conflicts.

    :param requires:
        Optional list of permission scopes required to update files of this entity. This
        argument not limit users from reading uploaded files (because usually most of files
        are readable by everyone), but instead, limit users from updating (uploading and
        replacing) files with given set of required permissions.

    :param readable:
        Optional list of permission scopes required to read files of this entity. Usually
        all uploaded files are accessible for all users, and application only limits who
        can update (upload, replace, delete) files. For the special case situation there
        is a posibility to limit - who can even read those uploaded files. This argument
        is used to that.

    :param app:
        Optional name of the parent application of this entity. If omitted - the current
        calling application will be used as the parent one.
    """

    app_name: str
    if app is not None:
        app_name = app
    elif '.' in name:
        app_name, name = name.split('.', 2)
    else:
        app_name = get_calling_app()
    entity = StorageEntity(
        app=app_name,
        name=name,
        requires=requires,
        readable=readable
    )
    entity_name: str = '.'.join([app_name, name])
    registered[entity_name] = entity
    logger.debug(f"registered file storage entity {CSTYLE['red']}{entity_name}{CSTYLE['clear']}")

