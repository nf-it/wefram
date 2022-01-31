Installation
============


The Wefram is based on two database engines, whose must be installed
on the machine where the platform executes at (those engines must be
accessible on both production server and the development machine where
programmer is working on):

* **PostgreSQL** database server for storing permanent data;
* **Redis** server, used for caching and for runtime data;

For the simple case, when databases are located toghether with the
project itself - you may install them locally.

.. note::

    This manual does not covers the installation and configuration of
    those database engines.


Installation variants
---------------------

There are two options on how to start with the Wefram platform:

* Using **docker** container as the core, with already installed and
  ready to use packages, both backend and frontend;
* By preparing the server's environment with yourself, installing
  Python virtualenv for backend environment, and NodeJS and Yarn
  for the frontend compilation. Corresponding steps will be shown
  below.


Docker-based installation
-------------------------

There is a docker container with already pre-built necessary to
use environment. To use it, as you may guess, the Docker Engine
must be installed on the machine where the project is developed
at.


Custom server installation
--------------------------

To start using the **Wefram** platform, first of all, there must
be resolved a pair of dependencies:

* **Python 3.9** or higher.
* **Yarn** and **nodeJS**.


For the example, if you using **Ubuntu** or **Debian** operating system:


.. code-block::

    sudo curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo bash -
    sudo apt install nodejs python3-venv
    sudo corepack enable


Now, we need to create the project's directory, where all applications
will be located at, and initialize the project.

.. code-block::

    mkdir my_project
    cd my_project
    python3 -m venv .venv
    source .venv/bin/activate
    pip install wefram
    create-wefram-project

After answering the set of common questions, we will get the ready to
build empty project. Let's build it using **setup** procedure.

Note that **setup** uses only once, on the first project start, because
this procedure drops all data in the corresponding Wefram database,
recreating it. At all other times you about to use **make** procedure,
which will be described later, in the **Getting started**.

.. code-block::

    ./manage setup

To run the test (development) server and try the empty project in
work - start the **server** script by Python interpreter and open
the http://localhost:8000/ URL in the browser.

.. code-block::

    python3 server.py

