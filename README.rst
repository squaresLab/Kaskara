.. -*-restructuredtext-*-

Kaskara
=======

.. image:: https://travis-ci.com/ChrisTimperley/Kaskara.svg?branch=master
    :target: https://travis-ci.com/ChrisTimperley/Kaskara

.. image:: https://badge.fury.io/py/kaskara.svg
    :target: https://badge.fury.io/py/kaskara

.. image:: https://img.shields.io/pypi/pyversions/kaskara.svg
    :target: https://pypi.org/project/kaskara


A simple, unified API for performing static analysis on programs in a variety
of languages. Kaskara avoids dependency hell when analysing programs by making
use of Docker.

* Kaskara currently provides C and C++ analysis support via its Clang driver,
* As of January 2020, Kaskara now provides support for Python analysis.
* Support for analysis of Java code is planned for February 2020.

.. image:: https://upload.wikimedia.org/wikipedia/commons/f/fc/Kaskara-Sword.jpg


Post-Installation
-----------------

After installing the `kaskara` package as a dependency of your project, you
should execute the following code to complete the installation by building the
support backends:

.. code:: python
  
    import kaskara
    kaskara.post_install()
