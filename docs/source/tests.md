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

def setup(data):
    pass

def test(data):
    pass

def teardown(data):
    pass

```

A test must implement at least a 'test' function that receives a data object as argument.


## Infile Test Data

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


## The Test and Code

Currently, the Web Module does not support parsing complex code structures (like *if*, *for* and *while*).
It is encouraged to move any complex code outside of the test and into Page Objects.
For better use of the Web Module, the test code should consist in calls to functions like Golem actions or page functions.

The Web Module does not support **imports** either.
So when saving a test from the Web Module import statements are dropped.