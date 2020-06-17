# Golem - Test Automation

[![Build Status](https://travis-ci.com/golemhq/golem.svg?branch=master)](https://travis-ci.com/golemhq/golem)
[![Documentation Status](https://readthedocs.org/projects/golem-framework/badge/?version=latest)](https://golem-framework.readthedocs.io/en/latest/?badge=latest)
[![Join the chat at https://gitter.im/golem-framework/golem](https://badges.gitter.im/golem-framework/golem.svg)](https://gitter.im/golem-framework/golem?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Golem is a test framework and a complete tool for browser automation.
Tests can be written with code in Python, codeless using the web IDE, or both.

**Tests can be written with the web app**
<p align="center">
    <img width="600" src="./images/test-case.png" />
</p>

**But, they are still Python code**
<p align="center">
    <img width="600" src="./images/example-test-code.png" />
</p>

## Batteries Included

* Multi-user web IDE
* Extended classes for [WebDriver](https://golem-framework.readthedocs.io/en/latest/golem_public_api/webdriver-class.html) and [WebElement](https://golem-framework.readthedocs.io/en/latest/golem_public_api/webelement-class.html)
* More than 200 self documenting [Actions](https://golem-framework.readthedocs.io/en/latest/golem-actions.html)
* [Webdriver-manager](https://github.com/golemhq/webdriver-manager) utility
* Built in parallel test support
* Reporting engine

<br>

**Golem is still in beta!**. Read the changelog before upgrading.

<br>

## Screen Captures

**Report Dashboard**
<p align="center">
    <img width="500" src="./images/report-dashboard.png" />
</p>

**Execution Report**
<p align="center">
    <img width="500" src="./images/execution-report.png" />
</p>

**Test Execution Detail**
<p align="center">
    <img width="500" src="./images/test-execution-detail.png" />
</p>

## Installation

Golem works with Python 3.5+

```
pip install golem-framework
```

Read the full installation guide here: [https://golem-framework.readthedocs.io/en/latest/installation.html](https://golem-framework.readthedocs.io/en/latest/installation.html)

## Quick Start

**Create a test directory anywhere in your machine**

```
golem-admin createdirectory <test_directory>
```

**Download the latest webdriver executables**

```
cd <test_directory>
webdriver-manager update
``` 

Webdriver executables are downloaded to the *drivers* folder. For more information check [this page](https://golem-framework.readthedocs.io/en/latest/browsers.html) of the documentation.

**Start the Web Module**

```
golem gui
```

The Web Module can be accessed at http://localhost:5000/

By default, the following user is available: username: *admin* / password: *admin*

**Run a Test From Console**

```
golem run <project> <test>
golem run <project> <suite>
```

Args:

* -b | --browsers: a list of browsers, by default use defined in settings.json or Chrome
* -p | --processes: run in parallel, default 1 (not parallel)
* -e | --environments: a list of environments, the default is none
* -t | --tags: filter tests by tags

## Documentation

[https://golem-framework.readthedocs.io/](https://golem-framework.readthedocs.io/)

## Questions

If you have any question please use the [Gitter channel](https://gitter.im/golem-framework/golem).

## Contributing

If you found a bug or want to contribute code please read the [contributing guide](https://github.com/golemhq/golem/blob/master/CONTRIBUTING.md).

## License

[MIT](https://tldrlegal.com/license/mit-license)

## Credits

Logo based on ["to believe"](https://www.toicon.com/icons/feather_believe) by Shannon E Thomas, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
