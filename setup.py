from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import sys

import golem


here = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='golem-framework',
    version=golem.__version__,
    description='Test automation framework for functional tests using Selenium',
    # long_description=long_description,
    url='https://github.com/lucianopuccio/golem',
    author='Luciano Puccio',
    author_email='me@mail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
    keywords='test automation framework selenium webdriver',
    packages=find_packages(),
    setup_requires=['setuptools-pep8'],
    install_requires=['Flask==0.12.2',
                      'Flask-login==0.4.0',
                      'selenium==3.6.0',
                      'requests==2.18.4',
                      ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['golem-admin = golem.bin.golem_admin:main']
    },
    cmdclass={'test': PyTest},
    include_package_data=True,
    platforms='any',
    test_suite='',
    extras_require={
        'testing': ['pytest'],
    }
)
