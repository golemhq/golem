Execution Module
==================================================

This module stores values specific to a single test execution.
These values should be read-only, modifying them can cause errors.

Location: golem.**execution**

**Example:**

test.py
```
from golem import execution
from golem.browser import open_browser


def test(data):
    print('Running test:', execution.test_name)
    open_browser()
    execution.browser.navigate('http://...')
    execution.logger.info('log this message')
```


## testdir

Golem root directory.

## project_name

Name of the project.

## project_path

Path to the project directory.

## test_name

Test name.

## test_dirname

The directory path where the test is located.

## test_path

Full path to the test file.

## settings

The settings passed to this test.

## environment

Name of the environment passed to the test.
None is no environment was selected.

## tags

The list of tags passed to the execution.

## report_directory

Path to the directory where the reports will be saved.

## browser

The current active browser. None if there is no open browser yet.

## browser_definition

The browser definition passed to this test.

## browsers

A dictionary with all the open browsers.

## steps

Steps collected by the test.

## data

The data object.

## secrets

The secrets data object.

## description

The description of the test.

## errors

A list of errors collected by the test.


## logger

Test logger object.

## timers

A dictionary with timers, used by the *timer_start* and *timer_stop* actions.
