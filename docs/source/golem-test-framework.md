Golem Test Framework
==================================================

<br>

# Test
A test contains a series of steps, input and output values and some assertions to determine if it passes or fails. 

## Test Components
A test is composed of the following elements:

#### Description
The description of the test. It is displayed in the report at the end.

#### Pages
A list of pages to import to the test.

#### Setup function
A function that is executed before the test

#### Test function
The test function itself

#### Teardown function
A function that is executed after the test even if it fails

<br>

# Test Suite
A test suite is a list of tests with the settings needed to run them (i.e.: the browsers, the environments, etc.)

## Suite Functions
A suite can define 4 functions:

### before_suite
It runs once at the beginning of the suite

### before_test
It runs before each test.

### after_test
It runs after each test

### after_suite
It runs once at the end of the suite



## Order of execution
Consider a test suite with 2 tests, the order of execution would be:

```
before_suite

# test 1
before_test
setup
test
teardown
after_test

# test 2
before_test
setup
test
teardown
after_test

after_suite
```

<br>

# Assertions

## Soft Assertions
Every assertion that starts with "verify" is a soft assertion, meaning that the error will be recorded, the test will be marked as failed at the end, but the test execution will not be stopped.

## Hard Assertions
Every assertion that start with "assert" is a hard assertion, meaning that it will stop the test execution at that point. The teardown method will still be executed afterwards.


## Assertion Actions example

### verify_element_exists(element):
- It adds an error to the error list
- test is not stopped


### assert_element_exists(element)
- It adds an error to the list
- The test is stopped, jump to teardown function
