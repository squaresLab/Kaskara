.. -*-restructuredtext-*-

Kaskara
=======

.. image:: https://badge.fury.io/py/kaskara.svg
    :target: https://badge.fury.io/py/kaskara

.. image:: https://img.shields.io/pypi/pyversions/kaskara.svg
    :target: https://pypi.org/project/kaskara

A simple library for performing static analysis on programs in a variety of languages for the purpose of program repair.
Kaskara avoids dependency hell when analysing programs by making use of Docker.

* Kaskara provides C and C++ analysis support via its Clang driver
* As of January 2020, Kaskara now provides support for Python analysis

.. image:: ./logo.png

Post-Installation
-----------------

After installing the `kaskara` package as a dependency of your project, you should execute the following code to complete the installation by building the support backends:

.. code:: python

    import kaskara
    kaskara.post_install()

Requirements
------------

* **WARNING:** The clang backend only works with glibc-based Docker images.
  Images that rely on an alternative libc implementation (e.g., Alpine relies on musl) are not supported.

Development
-----------

If you want to play with the Kaskara Clang backend from within a Docker container, you can use the following commands:

.. code:: bash

    make postinstall
    docker run --rm -v kaskara-clang:/opt/kaskara:ro -it your-image-name

This will first install Kaskara to a Docker volume, containing portable binaries and libraries, and then run a container with the volume mounted at `/opt/kaskara`.

You can also interact with Kaskara via the WIP command line:

.. code:: bash

    poetry run kaskara clang index \
        kaskara/examples:BehaviorTree.CPP \
        /workspace \
        /workspace/src/blackboard.cpp
