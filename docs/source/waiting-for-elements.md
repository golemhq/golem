Waiting for Elements
==================================================

## Implicit Wait

There is an implicit search timeout that is applied to every time a web element is searched.
This search timeout is defined in the settings file by using the [search_timeout](settings.html#search-timeout) setting key.

It can also be set by using the [set_search_timeout](golem-actions.html#set-search-timeout-timeout) and [get_search_timeout](golem-actions.html#get-search-timeout) actions.

Note that this timeout only waits for the element to be present (to exist in the DOM). It does not wait for the element to be visible, clickable, enabled, etc.


## Explicit Wait

There are a few ways to wait for an element to be present.

Using the [wait_for_element_present](golem-actions.html#wait-for-element-present-element-timeout-30) action:

```python
from golem import actions

actions.wait_for_element_present('#button-id', 15)
actions.click('#button-id')
```

Using the *timeout* argument in the find methods:

```python
from golem import actions

button = actions.get_browser().find('#button-id', timeout=15)
button.click()
```

Using the wait_for_element_present method of the WebDriver class:

```python
from golem import actions

actions.get_browser().wait_for_element_present('#button-id', timeout=15)
```

## Wait for Element Displayed

Very often an element needs to be displayed (visible) besides being present. Here are the ways to wait for an element to be visible.

Using the [wait_displayed](settings.html#wait-displayed) setting. This is defined globally for every search.

Using the [wait_for_element_displayed](golem-actions.html#wait-for-element-displayed-element-timeout-30) action.

Using the *wait_displayed* argument in the find methods:

```python
from golem import actions

actions.get_browser().find('#button-id', 15, wait_displayed=True).click()
```

Using the *wait_displayed* method of the WebElement class:

```python
from golem import actions

button = actions.get_browser().find('#button-id')
button.wait_displayed().click()
```