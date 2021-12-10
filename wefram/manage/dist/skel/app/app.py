from typing import *
from wefram.l10n import lazy_gettext
from wefram import aaa, ds, settings


# Note that you about to use 'lazy_gettext' for localization support in
# the app declaration, if needed! Do NOT use 'gettext', use 'lazy_gettext'
# instead here!


# A way to declare permissions into the app's permissions schema:

# aaa.permissions.register('some_permission', lazy_gettext("Some permission"))
# aaa.permissions.register('other_permission', lazy_gettext("Another permission", 'domain'))


# A way to declare storage entities for uploading files:

# ds.storages.register('default', requires=['some_permission'])
# ds.storages.register('another')


# A way to declare settings for the app:

# settings.register(
#     name='my_settings',
#     caption=lazy_gettext("My settings section"),
#     requires='some_permission',
#     properties={
#         'property1': settings.StringProp(lazy_gettext("The first property")),
#         'property2': settings.TextProp(lazy_gettext("The second property")),
#         'property3': settings.BooleanProp(lazy_gettext("The third property")),
#     },
#     defaults={
#         'property1': "Some default string value",
#         'property2': "Some default text",
#         'property3': True,
#     },
#     order=10
# )
#
# settings.register(
#     ...  # another settings section
# )

