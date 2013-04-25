Django app for managing the Bixi public bicycle sharing system's data from within Django projects.

It supports multiple cities out of the box.

Getting started
---------------

Requirements for django-bixi:

* django-tastypie
* south

These requirements are expressed in the pip-requirements.txt file and may be
installed by running the following (from within a virtual environment)::

    pip install -r requirements.txt

How to use
----------

From within your project's urls, expose the API resources of your choice as per django-tastypie's documentation at http://django-tastypie.readthedocs.org/en/latest/tutorial.html#adding-to-the-api

