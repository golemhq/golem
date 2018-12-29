Finding Elements
==================================================

## Actions and Elements

Golem actions that require a WebElement can be defined in three different ways:

An element tuple:

```python
from golem import actions

input = ('id', 'myElementId', 'Username input')
actions.send_keys(input, 'my username')

# the third element is optional
button = ('css', 'button.btn-default')
actions.click(button)
```

A css selector string:

```python
from golem import actions

actions.send_keys('#myElementId', 'my username')
actions.click('button.btn-default')
```

A WebElement object:

```python
from golem import actions

webelement = actions.get_browser().find(id='myElementId')
actions.send_keys(webelement, 'my username')

webelement = actions.get_browser().find(css='button.btn-default')
actions.click(webelement)
```


## find and find_all

The browser has two methods used to find elements: **find** and **find_all**

### find()

GolemExtendedDriver.**find**(*element=None, id=None, name=None, link_text=None, partial_link_text=None, css=None, xpath=None, tag_name=None, timeout=None, wait_displayed=None*)

The **find()** method provides a few ways to find elements.
Only one search criteria must be provided. *element* must be a CSS selector string, an element tuple or a WebElement object.

The *timeout* argument determines how much time to wait until the element is present.
If this is not provided, the value defined in settings by the *search_timeout* key will be used.
This is considered the global search timeout.

The *wait_displayed* argument makes **find()** wait for the element to be displayed (visible) as well.
This value is taken by default from the *wait_displayed* key in settings.

Some examples:

```python
from golem import actions


browser = actions.get_browser()

# by a tuple
element = browser.find(('id', 'someId'))

# by a css selector (positional argument) 
element = browser.find('input.someClass')

# by a WebElement object 
element = browser.find(id='someId')
element = browser.find(element)

# by css selector (keyword argument)
element = browser.find(css='input.someClass')

# by id
element = browser.find(id='someId')

# by name
element = browser.find(name='someName')

# by link text
element = browser.find(link_text='link text')

# by partial link text
element = browser.find(partial_link_text='link')

# by xpath
element = browser.find(xpath="//input[@id='someId']")

# by tag name
element = browser.find(tag_name='input')
```

### find_all()

GolemExtendedDriver.**find_all**(*element=None, id=None, name=None, link_text=None, partial_link_text=None, css=None, xpath=None, tag_name=None*)

Finds all the elements that match the selected criteria.
Only one search criteria must be provided. Returns a list of WebElements.
*element* must be a CSS selector string, an element tuple or a WebElement object.

```python
from golem import actions

browser = actions.get_browser()
table_rows = browser.find_all('table.myTable > tbody > tr')
```

## Finding children elements

WebElements also have the *find()* and *find_all()* methods. They can be used to find children elements from a parent element.

```python
from golem import actions

browser = actions.get_browser()

table_rows = browser.find('table.myTable').find_all('tr')

for row in table_rows:
    print(row.find('td.resultColumn').text)
```

## element() and elements() Shortcuts

**elemenent()** and **elements()** provide handy shortcuts to **find()** and **find_all()** respectively.

```python
from golem.browser import element, elements


title = element(id='headerTitle')
print(title.text)
 
table_rows = elements('table > tbody > tr')
print(len(table_rows))
```