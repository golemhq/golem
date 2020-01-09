Test data
==================================================

The data for each test can be stored inside the test or in a separate CSV file.
To select which location Golem should use, set the *test_data* setting to 'csv' or 'infile'.


## CSV Data

When *"test_data"* setting is set to "csv" the data will be saved in a separate csv file in the same folder as the test.

**Note**: All csv values are considered strings. If you need different value types use the 'infile' setting.


## Infile Data

When using *"test_data": "infile"* in settings different Python variable types can be used. **Strings must be defined in quotes in the Web Module data table**.

![data table infile](_static/img/data-infile.png "Test With Data Table")

The test code looks like this:

**test_with_infile_data.py**
```
description = 'Hey! this test has infile data!'

data = [
    {
        'numbers': 12,
        'boolean': False,
        'none': None,
        'list': [1,2,3],
        'dict': {'key': 'string'},
        'tuple': (1, '2', 3.0),
        'str_single': 'test',
        'str_double': "test",
    },
    {
        'numbers': 12,
        'boolean': True,
        'none': None,
        'list': ['a', 'b', 'c'],
        'dict': {"key": 12},
        'tuple': ('a', 'a"b"c', "a'b'c"),
        'str_single': 'a "b" c',
        'str_double': "a 'b' c",
    },
]

def test(data):
    navigate('some_url')
    send_keys(('id', 'searchInput'), data.str_single)
    
```

Infile data is stored as a list of dictionaries. Each dictionary is a different test set.


## Adding Values to Data at Runtime

Values can be added to the data object using the *store* action

```python
def test(data):
    store('title', 'My Title')
    assert_title(data.title)
```

## Accesing data during the test

Data object is present in the execution module during the test.

```python
from golem import execution

print(execution.data.my_value)
```

Data object is shared among *setup*, *test* and *teardown* functions:

```python
def setup(data):
    store('title', 'My Title')

def test(data):
   assert_title(data.title)
   
def setup(data):
   assert_title_is_not(data.title)
```

The *get_data* action can be used to retrieve the data object:

page1.py
```python
from golem import actions

def function():
    print(actions.get_data().title)
``` 

## Environments

Environments are defined in the *environments.json* file inside a project.
This file can be used to store environment specific data, such as the URL and the user credentials.

For example:

environments.json
```json
{
    "testing": {
        "url": "http://testing.app",
        "users": {
            "user01": {
                "username": "john"
            },
            "user02": {
                "username": "mark"
            }
        }
    },
    "staging": {
        "url": "http://stage.app",
        "users": {
            "user01": {
                "username": "john"
            },
            "user02": {
                "username": "mark"
            }
        }
    }
}
```

During the execution of the test, the environment data is stored in data.env:

test1.py
```python
def test(data):
    navigate(data.env.url)
    login(data.env.users.user01.username)
```

### Select the Environments For the Test

There are two ways to define the environment (or environments) for a test or suite:

1. from the command line:
    ```bash
    golem run project_name test_name -e testing
    golem run project_name suite_name -e testing staging
    ```

2. from the definition of a suite:
    
    suite1.py
    ```python
    environments = ['testing']
    ```
    
## Secrets

Secrets are defined in the *secrets.json* file inside a project.
Secrets can be used to store specific data which you do not want to expose in golem test reports / logging such as passwords, hostnames of database systems and temporary test data needed for text execution

*Please note:* When using secrets in conjunction with default Golem actions, their values can be exposed in the test reports and logs. Exposure is caused by the fact that most default golem actions log their actions.

**secrets.json**
```json
{
  "database": {
    "host": "db-server.local",
    "user": "db_consumer",
    "password": "abc",
    "port": 5432,
    "schema": "public"
  },
  "secret_user_1": "Joe"
}
```

During text execution secrets can be stored and retrieved, see examples below.

1. storing and retrieving a secret from a test
```python
def test(data):
    store_secret('password', 'my_password')
    print(get_secrets().password)
```

2. storing and retrieving a secret from a page
```python
from golem import actions
def some_function():
    actions.store_secret('password', 'my_password')
    print(actions.get_secrets().password)
```