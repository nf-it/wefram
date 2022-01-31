Wefram platform
===============

**Wefram** is the open source platform used to create complex web projects consisting of
both backend and frontend parts, allowing using both SSR (server-side rendering) using
template renders, and CSR (client-side rendering) using *React* based SPA (single page
application) approach.

The main point is to handle as much as possible repeating or taking much of time elements
of the development process by the platform (let's not name is "framework", okay?), giving
programmers time to make end-point code of corresponding project applications only.

The another goal of using Wefram is the ability of dividing the entire project into
applications, often independent on each other. This provides us the posibility to
write sometimes small, somethimes just funtion-resolving modules (applications) and
store them in the repository, and re-use when needed. You may see many analogies with
other module-based frameworks such as *Django* or *Flask*. But Wefram takes in work
a lightly much, then those frameworks, providing already pre-developed, ready to
use frontend SPA platform (React-based), and programmers of the project only focuses
on the target functional code of the project modules, not wasting time on the
frontend basics development, SSR & CSR integration into a single project, etc.


Approach
--------

The platform consists of itself (installed from *pypi* with *pip*) and developed and
enabled project's applications. So, the final project will have a set of modules, named
"applications", placed in the project's directory, and a set of backend and frontend
third-party packages (both for backend & frontend).


Provides
--------

The platform itself provides some most used functionality and facilities, ready
to use from the box, such as:

* **Applications' management**:  the project's modules, named *application* management, allowing 
  to install and deinstall project's apps, enable and temporary disable, and providing the dividing
  of the entire project on (most often) independent parts, with **dynamic inclusion and exclusion
  in and from the final build**.
* **Dependencies resolving**: application's and platform's dependencies summarizing and resolving,
  both for *backend* (Python with *pip*) and *frontend* (React@TypeScript with *yarn*).
* **PostgreSQL database** dialect and special types support.
* **State-based migration** with no needing of any kind of migration history or scripts generating.
* **In-memory database** (**Redis**) connectivity, caching facility, etc.
* **ORM** (Object relating modeling) with files storage transparent integration.
* **ORM history** facility with automated logging of changes in models' instances.
* **Files storage** for uploadable content with ready-to-use support from the platform side, including
  all routings and handlings.
* **Localization** *extended* facility with domains support both on backend and frontend.
* **Routing** facility for both HTTP(S) and WebSockets.
* **API** functionality out of box, with ready-to-use **ORM models DTO** allowing to make any 
  ORM model API-ready in really two lines of code.
* **Template rendering** for SSR (server-side rendering) using *Jinja2* template engine.
* **Frontend** ready-to-use **React** implementation.
* **Material-UI** implementation with extended set of common purpose components.
* **User interface** out of box, with no need to code anything from the scratch, with the theming facility.
* **Settings** ready-to-use facility (the application is not required to have the own implementation).
* **Users & roles facility** out of box - Authentication, Authorization and Accounting, roles' permissions
  management, etc.
* **Permissions** handling out of box for most entities, such as *API*, *Views*, *Screens*, *Settings*, etc.
* **CLI** (command-line interface) basics to implement command line management facilities.
* **Notifications** (displayed to users), messages transports between backend and frontend.
* **Sidebar** and **Sidemap** automated facility.
* **Screens** (client-side rendered) facility, even **managed screens** with backend runtime qualifications.
* **Typo screens automatisations** to exclude needing of writting any line of the
  'React @ TypeScript' code for very common cases.


As been said - the platform aims to make programmers work on the corresponding project's
code.


Written on
----------

Like any client-server project, the Wefram-based project will consist of two main
parts:

* Backend, which is written in **Python 3**.
* Frontend, which is written mainly in **TypeScript & React** or **templated HTML**.

The frontend part is lightly more interesting than just a TypeScript or just a
React. While we speak about two variants of render - SSR & CSR, we about to
handle two different approachs.

If we speak about regular, search engines (Google, Yandex...) indexing site - 
we usually speak about SSR with pre-rendered HTML code returning to the browser.
Wefram uses *Jinja2* template engine to render the HTML on the server side. To
provide assets like CSS, JS scripts and so on, the Wefram uses assets approach,
which makes possible to build assets from all enabled applications into understandable
and easy to use structure, which can be directly handled by the web server like
*nginx* or *apache*.

If we speak about site's administrative panel, about corporate portal, about some another 
kind of business logics, used primary on workplaces - we speak about SPA (single page
application), we speak about CSR (client-side rendering), about traffic economy, reusing
same pre-built program code by clients' browsers without needing of reloading everything.
Here we speak about *React* which is based (in our configuration) on *TypeScript*.

The Wefram combines both described above approachs into one project. This means that
a single project may have both SSR and CSR applications, modules, etc. This allows
not to divide a project into independent parts, combining all in one place.

This not requires, for example, the project to have SSR pages. Wefram gives this
posibility, but only when the project needs it. For example, if we have a regular
site, for example with a set of services for the end user, and we want to make
a some kind of reservation system for those services - we will make several
SSR pages (to be easyly indexed by search engines) basing on Jinja2, HTML,
CSS and pure JS; and make a workspace for employee, administering those reservations
and services, with CSR using *React & TypeScript*.


Applications
------------

While many projects divides the entire project horizontally - to the "all backend"
and "all frontend", the *Wefram* uses another approach - it dividing the entire
project vertically, to "modules", names "applications".

The every application consists of backend part (even almost empty) and optional
frontend part. Why the frontend is optional? Because (a) the application may handle
some work without any client side control (for example, make regular integration with
another service, or give a facility on, for example, sending messages via Telegram),
and (b) because Wefram gives several interesting backend-realized approachs, whose
may exclude needs of frontend programming for simple tasks (for example, the
applicaion's programmer relieved of the need to make settings, properties handling,
administering simple database models on the frontend and so on).

So, while the application consists of both backend and frontend, it makes much
easier to install to the project and deinstall from the project applications,
developing application outside the main project and then easily adding it to
the project, etc. **The point is that makes much easily to divide the entire project
into reusable and often independent parts.**


Localization
------------

One of the main our targets was to make the platform localization-ready from the
begining, as one of main goals. Because of this, everywhere, where that is possible,
we made the localization interfaces and interesting localization approach. We will
speak about it in the documentation, in the separate section.


Where we are
------------

The Wefram is in active development and about 80% ready to be published. Much
of work on documenting is still in progress (which take a lot of time), some
interesting ideas are in progress.

But several really living projects are already in live, already basing on the
Wefram platform and successfully working.



