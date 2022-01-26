"""
Provides the user interface types and classes.
"""

from typing import *
from ..requests import HTTPException, HTMLResponse, PrebuiltHTML
from ..tools import JSONexactValue
from .l10n import L10nStr


__all__ = [
    'BaseScreen'
]


class BaseScreen:
    """
    The project-registered screen's abstract class. This class implements most of the methods
    and properties used by all project screens.

    The project screen is a client-side rendered entity which visualizes... anything. The
    anything that programmer want to give to the end-user as a user interface of the
    one or the another application.

    The screen, in opposite to the ``View``, renders on the client side, using React and
    compiled JavaScript. Each screen is routed by the corresponding routing path and
    corresponds to that path. This means that if the user type (or copy-paste, or click
    the link) the URL of the screen in the browser's address bar and click "Go" (or press
    "Enter" key) - the corresponding screen will open.

    The main point of screen design, in general (not taking in account special cases), is
    making the screen as frontend code (using TypeScript as programming language and
    React as user interface base framework). On the backend side screens usually only
    declares, giving the platform only knowledge about "hey, we have a screen, and it must
    be routed, okay?".

    So, summarizing:

    * **Backend** usually has only the screen's definition - the name, set of required
      permissions, routing path, sitemap registering, etc.
    * **Frontend** has the actual program code for screen render, interaction, etc.

    The another important apporach is that screens compiles independently and represents
    by independent compiled JavaScript files. The screen, the one or the another, loads
    only when it is needed. This means that client's browser known nothing about executable
    JS of the screen before the user try to open that screen. Only at a moment when user
    opens the screen - the platform code request the backend for the corresponding JS
    code, load it and execute. This provides both traffic and client browser resources
    economy.
    """

    _root_component: str
    _route_url: str
    _route_params: List[str]
    _requires: List[str]

    screen_class: Literal['Screen', 'ManagedScreen', 'CompositeScreen'] = 'Screen'

    name: str
    """ The system name of the screen. """

    app: str
    """ The screen's parent application name. """

    route: str = None
    """ The screen route path. Used to automatically add the screen in the routing table
    of the project. """

    component: Optional[str] = None
    """ The path to the screen's frontend component (the TypeScript file with the screen code).
    If the path is a relative one - the component will be searched basing from the screen's
    application directory; otherwise - rooting from the project root directory.
    
    For example, if the application name is 'myapp' and the component is ``containers/MyScreen``,
    then the screen's (.tsx) file expects to be placed at ``myapp/containers/MyScreen.tsx``.
    
    The screen coding is described in the platform manuals, it is best to read it.   
    """

    caption: Optional[Union[str, L10nStr]] = None
    """ The screen's caption used as human-readable name. """

    parent: Optional[str] = None
    """ The optional name of the sitemap parent item. Used when the screen's sitemap button is 
    about to be placed within the some sitemap folder. The name of the corresponding folder
    item is expected here. """

    icon: Optional[str] = None
    """ The screen's icon (which will be rendered in the sitemap). The absolute URL is expected.
    It may be made with :py:func:`wefram.urls.asset_url` function for the assets-stored images. """

    order: Optional[int] = None
    """ The order in which this screen will appear in the sitemap and some other places (such as
    settings screen, for example). """

    requires: Optional[List[str]] = None
    """ Optional list of permission scopes required to current user have to access the screen. """

    params: Any = None
    """ The specific for the screen set of parameters. Usually is used by inheritted special case
    screen classes used as base for target, end screens. """

    def __init__(self):
        from ..aaa import permitted

        requires: List[str] = self._requires
        if requires and not permitted(requires):
            raise HTTPException(403)

    @classmethod
    async def endpoint(cls, *_) -> HTMLResponse:
        """ The default endpoint of the screen. Used when the client side browser open the
        workspace by the screen's URL to return the initial SPA HTML page and only then
        load the screen.
        """

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
        """ Returns the screen static schema. Used at the ``make`` process to make the
        static screens' linking.
        """

        return {
            'app': cls.app,
            'name': cls.name,
            'screenClass': cls.screen_class,
            'rootComponentPath': cls._root_component,
            'rootComponent': cls._root_component_predef(),
            'requires': cls._requires,
            'routeUrl': cls.get_route_url(),
            'routeParams': cls._route_params,
            'params': cls.params or {}
        }

    @classmethod
    def runtime_json(cls) -> dict:
        """ Returns the runtime screen struct. """

        return {
            'caption': str(cls.caption)
        }

    @classmethod
    def get_route_url(cls) -> str:
        """ Returns the screen routing path. """

        return getattr(cls, '_route_url')
