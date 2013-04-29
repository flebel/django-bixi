Django app for managing data from the Bixi public bicycle sharing system.

It supports multiple cities out of the box.

Getting started
---------------

Requirements for django-bixi:

* django-tastypie
* south (required if you plan on using the migrations)

These requirements are expressed in the pip-requirements.txt file and may be
installed by running the following (from within a virtual environment)::

    pip install -r requirements.txt

Configuration
-------------

django-bixi ships with throttling built in. The following options have to be
set in your project's settings.py, as per the documentation:
http://django-tastypie.readthedocs.org/en/latest/throttling.html#throttle-options

* BIXI_THROTTLE_AT
* BIXI_TIMEFRAME
* BIXI_EXPIRATION

How to use
----------

From within your project's urls, expose the API resources of your choice as per django-tastypie's documentation at http://django-tastypie.readthedocs.org/en/latest/tutorial.html#adding-to-the-api

