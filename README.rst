Part of `edX code`__.

__ http://code.edx.org/

edx-reverification-block
========================

An XBlock for in-course reverification.


Overview
--------

This XBlock prompts a user to complete in-course reverification.  During in-course reverification, the user submits a photo of his or her face.  An external service then compares this photo to a photo of the user's government-issued ID, which the user submitted at the beginning of a course.


Prerequisites
-------------

For local development, you will need:

* `Python <https://www.python.org/>`_ (most systems have this installed by default)
* `pip <https://pip.pypa.io/en/latest/installing.html>`_ (a package manager for Python)
* `NodeJS <https://nodejs.org/download/>`_


Getting Started
---------------

Install requirements:

.. code:: bash

    make install

Run the development server:

.. code:: bash

    make workbench

Run the unit test suite:

.. code:: bash

    make test


Sass Compilation
----------------

If you change any Sass file, you MUST update the CSS and check the compiled CSS into the repository!
(This allows us to deploy the XBlock to a runtime without requiring the runtime to have NodeJS installed.)

To compile sass:

.. code:: bash

    make compile-sass

Then check the updated ".css" files into the repository.


License
-------

The code in this repository is licensed under LICENSE_TYPE unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though it was written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org

Mailing List and IRC Channel
----------------------------

You can discuss this code on the `edx-code Google Group`__ or in the
``#edx-code`` IRC channel on Freenode.

__ https://groups.google.com/forum/#!forum/edx-code
