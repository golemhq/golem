# Contributing to Golem

Thank you for your interest in contributing to Golem!

## Questions

If you have a question please use the Gitter channel: https://gitter.im/golem-framework/golem

## Submitting a Bug

When reporting new bugs, please make sure that the report includes as much information as possible. Not all of the following is required, it depends on the issue.

- A reproducible test case
- Golem version
- Operating System and Python version
- Selenium version
- Webdriver version
- Browser version
- Screenshot, traceback, or log

Please note: Always try to use the latest version of Selenium, the Webdriver executables, and the browsers before raising a bug.

## Suggestions

Enhancements and new feature ideas are welcome, however, time is limited. We encourage people to try and submit a pull request. Read how to do that below.

## How to Contribute Code

If you have improvements or fixes for Golem, send us your pull requests! For those
just getting started, Github has a [howto](https://help.github.com/articles/using-pull-requests/).

## Development Guide

### Running Unit Tests

```
pip install pytest
pytest run tests
```

To run only fast tests use the following command:

```
pytest run tests --fast
```

### Running Integration and UI tests

Golem has suites for integration and UI tests. The steps to run them can be found here: https://github.com/golemhq/golem-tests

### Code Style

The code style for the project is [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following additions:

- Line length limit is extended to 90 characters
- Line length can exceed 90 characters if readability would be reduced otherwise
- Single quote strings are preferred unless the string itself contains a single quote.

### Building the Docs

```
pip install sphinx
pip install recommonmark
cd docs
make html
```
