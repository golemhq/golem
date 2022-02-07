Test data
==================================================

A test file can have one of three different types of data sources: CSV, JSON and internal.


## CSV Data

The CSV data file must have the same filename as the test file and be located in the same folder.
Note that: All CSV values are considered strings.
If you need different value types use JSON or internal data.

**test_01.csv**
```
name,age
John,23
Marie,32
```

**test_01.py**
```python
def test(data):
    print(data.name, data.age)
```

## JSON Data

The JSON data file must have the same filename as the test file and be located in the same folder.
Valid JSON data must be an object (dictionary), or an array of objects (list of dictionaries).
Invalid data is ignored.

**test_02.json**
```json
[
   {
      "item_id": 5143,
      "price": 2134.55,
   },
   {
      "item_id": 8429,
      "price": 462.21,
   }
]
```

**test_01.py**
```python
def test(data):
    print(data.item_id, data.price)
```

## Internal Data

Internal data must be a variable with name "data" defined inside the test file and of type either dictionary or list of dictionaries.

**test_03.py**
```python

data = [
    {
        'name': 'Chicken S Rice',
        'price': 100,
        'discount': True
    },
    {
        'customer': 'Paneer Schezwan Rice',
        'price': 110 
        'discount': False,
    },
]

def test(data):
    print(data.name, data.price, data.discount)
    
```

## Repeating the test based on data

When the data is a list (or array) with more than one item, or a CSV table with more than one row,
the test will repeat once per each test data set.

## Adding Values to Data at Runtime

Values can be added to the data object using the *store* action.

```python
def test(data):
    store('title', 'My Title')
    assert_title(data.title)
```

## Accesing data during the test

The data object is present in the execution module during the test.

```python
from golem import execution

print(execution.data.my_value)
```

The data object is shared among all the test functions of a test file:

```python
def setup(data):
    store('title', 'My Title')
    data.username = 'my-username'  # direct assignment also works

def test_one(data):
    assert_title(data.title)
    assert_username(data.username)
   
def test_two(data):
    assert_title_is_not(data.title)
    assert_username_is_not(data.username)
```

The *get_data* action can be used to retrieve the data object:

**page1.py**
```python
from golem import actions

def function():
    print(actions.get_data().title)
``` 

## Environments

Environments are defined in the *environments.json* file inside a project.
This file can be used to store environment specific data, such as the URL and the user credentials.

For example:

**environments.json**
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

**test1.py**
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
    
    **suite1.py**
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