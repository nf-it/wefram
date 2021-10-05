Reserved ORM attribute names
============================


Like SQL itself, in addition to the SQL standard, there are
several words whose you have to avoid to use as model's column
names. This is because those words are reserved by the ORM
itself, including methods and special symbols. Let's list
them here, in one place for your cconvenience.

Note that using any of SQL (especially PostgreSQL) keywords
is really a bad idea. For example, using keywords like
``limit``, ``offset``, ``order``, ``in``, ``group`` and
another like those - is not recommended.

Note also that the Wefram developers, when speaking about
[ds.Model] class, selects names for methods basing on the
reserved SQL keywords. This makes more keywords available
for columns naming for you, because we take words those
you wantn't use in column names anyway... say, ``create``
or ``select``. Not always we can find appropriate keyword
in the list of the SQL reserved ones (for example, the
method ``delete_where``, of cource, is not in the list),
but the reserved is in the priority.

Reserved words (in addition to PostgreSQL reserved ones):
    * ``Meta``
    * ``all``
    * ``create``
    * ``delete``
    * ``delete_where``
    * ``dict``
    * ``fetch``
    * ``first``
    * ``ilike``
    * ``json``
    * ``get``
    * ``key``
    * ``like``
    * ``update``
    * ``select``

Also, avoid using declared in the [ds.Model] class private
methods (whose names starts with '_') and special names
(whose names starts and ends with '__'). For example, the
[ds.Model] class has reserved names ``__pk__``, ``__pk1__``
and etc.
