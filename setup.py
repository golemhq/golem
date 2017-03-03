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

long_description = read('README.md')

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
    install_requires=['Flask==0.10.1',
                      'Flask-login==0.3.2',
                      'selenium==3.0.2',
                      'Pillow>3.3.1',
                      'pytest'],
    #scripts=['golem/bin/golem-admin.py'],
    entry_points={
        'console_scripts': ['golem-admin = golem.bin.golem_admin:main']
    },
    cmdclass={'test': PyTest},
    author_email='mail@lucianopuccio.com',
    description='Test automation framework for functional test automation written in python and using Selenium as automation engine tool',
    long_description=long_description,
    packages=['golem'],
    include_package_data=True,
    platforms='any',
    test_suite='',
    classifiers=[
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
