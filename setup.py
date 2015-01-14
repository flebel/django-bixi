#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='bixi',
      version='1.1',
      description='Django app for managing data from the Bixi public bicycle sharing system.',
      author='Francois Lebel',
      author_email='francoislebel@gmail.com',
      url='https://github.com/flebel/django-bixi/',
      packages=find_packages(),

      test_suite='setuptest.setuptest.SetupTestSuite',
      tests_require=(
        'django-setuptest',
        # Required by django-setuptools on Python 2.6
        'argparse'
      ),
)
