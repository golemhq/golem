Test Framework
==================================================

## Test

A test contains a series of steps, input and output values and some assertions or verifications to determine if it passes or fails. 

### Test Components

A test is composed of the following elements:

#### Description

The description of the test. It is displayed in the report at the end. Optional.

#### Data

Data can be defined inside the test. It can be a dictionary or a list of dictionaries.
In the latter scenario, the test will be run once per dictionary (test set). See [Test Data](test-data.html).

#### Pages

A list of pages to import to the test.

#### Setup Function

A function that is executed before the test.

#### Test Function

The test function itself. This is the only required element for the test. Everything else is optional.

#### Teardown Function

A function that is executed after the test even if there are exceptions or errors in setup or test.

### Example

```python

description = 'the description for my test'

pages = ['login', 'menu', 'releases']

def setup(data):
    navigate(data.env.url)
    login.login(data.env.user1)

def test(data):
    menu.navigate_to('Releases')
    data.store('release_name', 'release_001')
    releases.create_release(data.release_name)
    releases.assert_release_exists(data.release_name)

def teardown(data):
    releases.remove_release(data.release_name)
```

### Order of Execution

The order of execution is: setup, test, teardown.
If there are any exception errors in setup, then the test function will not be executed.
The teardown function is executed even if there were exceptions or errors in setup or test. 

## Test Results

The test can end with one of the following result statuses:

**Success**: The test run without any errors.

**Failure**: The test threw an AssertionError.

Possible reasons for a test to end with failure:
* Actions that start with 'assert_'.
  ```python
  actions.assert_title('My App Title')
  ```
* A call to *fail()* action.
    ```python
    actions.fail('this is a failure')
    ```
* A normal Python assert statement.
    ```python
    assert browser.title == 'My App Title', 'this is the incorrect title'
    ```

**Error**:

The test had at least one error. Possible reasons for errors:
* Actions that start with 'verify_'.
* An error added manually:
    ```python
    actions.error('my error message')
    ```  

**Code error**:

Any exception that is not an AssertionError will mark the test as 'code error'.

Example:

test1.py
```python
def test(data):
   send_keys('#button', 'there is something missing here'
```

```bash
>golem run project1 test1
17:55:25 INFO Test execution started: test1
17:55:25 ERROR SyntaxError: unexpected EOF while parsing
Traceback (most recent call last):
  File "C:\...\testdir\projects\project1\tests\test1.py"
SyntaxError: unexpected EOF while parsing
17:55:25 INFO Test Result: CODE ERROR
```

## Assertions and Verifications

### Soft Assertions

Every action that starts with "verify" is a soft assertion, meaning that the error will be recorded. The test will be marked as 'error' at the end, but the test execution will not be stopped.

### Hard Assertions

Every action that starts with "assert" is a hard assertion, meaning that it will stop the test execution at that point. The teardown method will still be executed afterward.

### Assertion Actions Example

**verify_element_present(element)**:
- It adds an error to the error list
- Logs the error to console and to file
- Takes a screenshot if *screenshot_on_error* setting is True
- The test is not stopped.
- The test result will be: 'error'

**assert_element_present(element)**:
- An AssertionError is thrown
- It adds an error to the list
- Logs the error to console and to file
- Takes a screenshot if *screenshot_on_error* setting is True
- The test is stopped, jumps to teardown function
- The test result will be: 'failure'
