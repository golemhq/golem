[![Build Status](https://travis-ci.org/lucianopuccio/golem.svg?branch=master)](https://travis-ci.org/lucianopuccio/golem)
[![Documentation Status](http://readthedocs.org/projects/golem-framework/badge/?version=latest)](http://golem-framework.readthedocs.io/en/latest/?badge=latest)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)


Golem - Test Automation Framework
==================================================
>Automate end to end tests in seconds, not hours.


Intro
--------------------------------------

Golem is a test automation framework for functional tests. It has a web module that enables easy and intuitive test crating. Implements the best practices in test automation the Page Object and data parametrization. It can run tests in parallel, in multiple browsers and with multiple data sets. It comes out of the box with a detail web reports engine. 

[comment]: <>


Installation
--------------------------------------

Golem works with Python 3.4+

```
pip install golem-framework
```

Quick Start
--------------------------------------

Create a test directory anywhere in your machine:

```
golem-admin createdirectory <directory_name>
```

Start the Web Module:

```
python golem.py gui
```

The Web Module can be accessed at http://localhost:5000/

By default, the following user is available: username: *admin* / password: *admin*


Documentation
--------------------------------------

Read the full documentation here: [http://golem-framework.readthedocs.io/](http://golem-framework.readthedocs.io/)
