from typing import *
from wefram.l10n import lazy_gettext
from wefram.ui import sitemap, screens
from wefram.urls import asset_url


# Note that you about to use 'lazy_gettext' for localization support in
# the screens declaration, if needed! Do NOT use 'gettext', use 'lazy_gettext'
# instead here!


# An example of sitemap folder declaration. The folder may be used to store
# several child screen buttons in it. Use 'parent' property of the
# 'screens.Screen' class to specify the corresponding folder.

# sitemap.append(
#     name='my_sitemap_folder',
#     caption=lazy_gettext("My folder"),
#     icon=asset_url('icons/my_folder_icon.svg'),
#     requires='some_permission',
#     order=100
# )


# An example of sitemap-registered screen is located below:

# @screens.register(sitemap=True)
# class MyVeryScreen(screens.Screen):
#     component = 'frontend/containers/MyVeryScreen'
#     route = '/veryscreen'
#     caption = lazy_gettext("The my very screen")
#     requires = 'some_permission'
#     order = 10


# An example of free-driven screen without sitemap registration

# @screens.register
# class MyFreeScreen(screens.Screen):
#     component = 'frontend/containers/MyFreeScreen'
#     route = '/some-free-screen'
#     caption = lazy_gettext("The my free-driven screen")
#     requires = 'some_permission'


# An example of the screen registered inside the sitemap folder.

# @screens.register(sitemap='my_sitemap_folder')
# class MyChildScreen(screens.Screen):
#     component = 'frontend/containers/MyChildScreen'
#     route = '/the-child-screen'
#     caption = lazy_gettext("The my sub-screen")
#     requires = 'some_permission'
#     parent = 'my_sitemap_folder'
#     order = 20

