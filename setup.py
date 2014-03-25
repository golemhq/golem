#! /usr/bin/env python

from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import golem

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGES.txt')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='golem',
    version=golem.__version__,
    url='http://github.com//',
    license='TBD',
    author='Luciano Puccio',
    tests_require=['pytest'],
    install_requires=['Django==1.6.1',
                      'Jinja2==2.7.2',
                      'MarkupSafe==0.18',
                      'Pygments==1.6',
                      'Sphinx==1.2.1',
                      'colorama==0.2.7',
                      'cov-core==1.7',
                      'coverage==3.7.1',
                      'docutils==0.11',
                      'py==1.4.20',
                      'pytest==2.5.2',
                      'pytest-cov==1.6',
                      'selenium==2.40.0'],
    scripts=['golem/bin/golem-admin.py'],
    cmdclass={'test': PyTest},
    author_email='mail@lucianopuccio.com',
    description='Test automation framework for functional test automation written in python and using Selenium as automation engine tool',
    long_description=long_description,
    packages=['golem'],
    include_package_data=True,
    platforms='any',
    test_suite='golem.test',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: QA Engineers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
