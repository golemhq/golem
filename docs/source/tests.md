Tests
==================================================

A test in Golem is a Python file. It must be located in the *tests* folder of a *project* in the Test Directory.
To create a Test Directory and a project follow [these steps](tutorial-part-1.html#create-a-test-directory) and [these steps](tutorial-part-1.html#create-a-new-project).

A test can be created from the Web Module or using the following command:

```bash
golem createtest project_name test_name
``` 


## Test Structure

```python

description = ''

tags = []

pages = []

skip = False


def setup(data):
    pass


def test(data):
    pass


def teardown(data):
    pass
```

A test must implement at least a **test** function that receives a data object as argument.


## Test Data

Test data can be defined inside the file or in a separate CSV file.
For detailed info about see: [Test Data](test-data.html) 

### CSV Data

It should be defined in a CSV file with the same name and in the same folder as the test.

### Infile Test Data

A test can have data defined as a list of dictionaries.

```python

data = [
    {
        'url': 'http://url1.com',
        'title': 'title1'
    },
    {
        'url': 'http://url2.com',
        'title': 'title2'
    }
]

def test(data):
    navigate(data.url)
    assert_title(data.title)
```

Note: when saving a test using the Test Module, if the *test_data* setting is not 'infile', any data stored in the test will be moved to a CSV file.

## Skip flag

A flag variable to indicate that this test should be skipped.
It should be a boolean or a string to use as skip message.
Note: tests will only be skipped when running from a suite.

## Tags

A list of tags (strings).
Tags can be used to filter tests when running a suite.
See [Filter Tests by Tags](running-tests.html#filter-tests-by-tags).

## Implicit vs Explicit Imports

By default the test runner imports the golem.actions module and any page module implicitly during the execution.
Pages are saved as a list of strings.
The GUI test builder complies with this format and generates code like the following:

```python
pages = ['page1']


def test(data):
    navigate('https://...')
    page1.custom_funtion()
```

This behaviour can be turned off by setting [implicit_actions_import](settings.html#implicit-actions-import) and [implicit_page_import](settings.html#implicit-page-import) to false.

Then, the test structure will be:

```python
from golem import actions

from projects.<project_name>.pages import page1


def test(data):
    actions.navigate('https://...')
    page1.custom_funtion()
```


### GUI Test Builder and Imports Statements

The GUI test builder only supports import statements for the **golem.actions** module and any Python module
inside the **pages** folder; and only when the implicit modes are turned off.
Any other import statements will be discarded when saving a test from the GUI test builder.