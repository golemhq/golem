Execution Module
==================================================

This module stores values specific to a test file execution.
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

## test_file

Module path of the current test file, relative to the tests folder.

## browser

The current active browser object. None if there is no open browser yet.

## browser_definition

The browser definition passed to this test.

## browsers

A dictionary with all the open browsers.

## data

The data object.

## secrets

The secrets data object.

## description

The description of the test.

## settings

The settings passed to this test.

## test_dirname

The directory path where the test is located.

## test_path

Full path to the test file.

## project_name

Name of the project.

## project_path

Path to the project directory.

## testdir

Golem root directory.

## execution_reportdir

Path for the execution report.

## testfile_reportdir

Path for the test file report

## logger

Test logger object.

## tags

The list of tags passed to the execution.

## environment

Name of the environment passed to the test.
None is no environment was selected.

## Values for each test function

### test_name

Current test function name.

### steps

Steps collected by the current test function.

### errors

A list of errors collected by the test function.

### test_reportdir

Path for the test function report.

### timers

A dictionary with timers, used by the *timer_start* and *timer_stop* actions.
