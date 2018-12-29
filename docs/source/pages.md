Pages
==================================================

A page in Golem is a module that can be imported into a test.
It can be used as a Page Object.

## Page Elements

A way to store element selectors in a page is by using a tuple.
This is the default behavior for the Web Module.

```python
input = ('id', 'myID', 'My Input')
button = ('css', 'button.btn-default', 'My Button')
```

The third value in the tuple is optional and it is used as a friendly name by the execution report.

## Page Functions

A page can have functions and these will be available from the test after importing the page into it.
These functions will also be available when using the Web Module as regular actions do.

**Example 1:**

page1.py
```python
from golem.browser import element

title = ('css', 'h1')

def assert_title(expected_title):
    assert element(title).text == expected_title 
``` 

test1.py
```python
pages = ['page1']

def test(data):
    navigate('http://...')
    page1.assert_title('My Expected Title')
```

**Example 2:**

page2.py
```python
from golem.browser import elements

table_rows = ('css', 'table > tbody > tr')

def assert_row_amount(expected_amount):
    rows = elements(table_rows)
    assert len(rows) == expected_amount, 'Incorrect amount of rows'
```

test2.py
```python
pages = ['page2']

def test(data):
    navigate('http://...')
    page2.assert_row_amount(5)
```