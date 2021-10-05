Data storage
============


The every project about to store some data in different storages.
Every user, role, every data object, every uploaded file or
image - stores in the corresponding data storage. The Wefram
based project uses different types of them. Let's speak about
them in general and about each of them in single.


Introduction to data storage
----------------------------

Storing different data in the Wefram-based project can be divided
into three basics:

#.  Storing object of models (rows in the relational database). Lets
    name it **ORM**.

#.  Storing uploadable files, images and etc. Lets name
    it **File storage**.

#.  Storing temporary or caching data in the interprocess memory.
    Redis in used for this, so let's name it **Redis**.


.. toctree::
    :caption: Detailing storages:
    :maxdepth: 1
    :titlesonly:

    ds/orm
    ds/models
    ds/reserved


Relational database storage
---------------------------

Wefram uses ORM and model-based presentation of corresponding
rows in the corresponding database tables. This means that
programmer about to deal not with raw SQL queries when
programming the project logics, but deal with Python classes
whose describing corresponding database rows.

Wefram basing on the SQLAlchemy ORM and PostgreSQL relational
database server (more precisely PostgresPro with JSONB included).

More about how to use relational databases: :ref:`ds_orm`. The
even more may be read at :ref:`ds_models`



File storage
------------

Often the project requires some files to be able to be uploaded,
replaced, deleted, and, of cource, downloaded or displayed.

Generally speaking, we can divide all
situations into two special cases:

#.  Single file storing. For example, we have an model describing
    some contact, with name, phone, and (interesting for us in
    this case) an avatar. The avatar, of cource, may be set by
    uploading some image.

#.  Multiple file storing within one entity. The most close
    realistic example is storing photos within a single album.
    So, there are several files uploaded, cooperated in one
    undestable entity.

Not matter which case we about to solve - we always will deal
with **file storage**. This is how Wefram stores and gives
posibility to access files.

Uploading files are stored within file system of the server
where Wefram based project is running at, at the special
root-based directory (by default named *files*).


Redis
-----

The *Redis* is used for interprocess...

