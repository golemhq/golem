Golem Public API
==================================================

<br>

## golem.actions

Contains a list of handy functions that are autococumenting and cover a large amount of possible actions and tasks. 


```
from golem import actions

actions.navigate('http://someurl.com/')
actions.send_keys('#searchInput', 'some search term')
actions.click('#submitButton')
actions.verify_text_in_element('#title', 'some title')

```

See the full [list of golem actions](golem-actions.html)

<br>

## golem.browser

Contains methods for interacting with a browser (a selenium webdriver instance)


### golem.browser.**open_browser(browser_id=None)**

Opens a new browser window. The browser_id is optional but useful when having multiple browsers open at the same time.

**Chosing a browser**

The browser that is selected follows this order of priority:

1. Command line *run* command, -b / --browsers flag
2. 'browsers' list defined in a suite
3. settings.json, "default_browser" option

Example:

```
python golem.py run project test -b chrome firefox
```


**The extra browser methods:**

#### browser.**find**([element, id, name, text, link_text,partial_link_text, css, xpath, tag_name, timeout])

Finds a webelement with the provided selector criteria. Every paramenter is optional but one selector must be provided. Timeout is also optional, by default, it uses the "implicit_wait" option defined in the settings.json

Returns a selenium webelement with two extra methods: *find()* and *find_all()*

#### browser.**find_all**([element, id, name, text, link_text,partial_link_text, css, xpath, tag_name])

Finds all webelements that matches the provided selector criteria. Every paramenter is optional but one selector must be provided. 

Returns a list of webelements that can be empty if no element matched the criteria. Each webelement in the list has two two extra methods: *find()* and *find_all()*



#### Example Usage of find() and find_all()

Consider the following HTML elements:

```
<div>
    <input id="someId" class="someClass" name="someName">
    <span>some text</span>
    <a href="">some link text</a>
</div>
```

The different ways to find this element are:

```python
from golem.browser import get_browser

browser = get_browser()

# by a tuple
element = browser.find(('id', 'someId'))

# by css selector
element = browser.find('.someClass')

# by id
element = browser.find(id='someId')

# by name
element = browser.find(name='someName')

# by text
element = browser.find(text='some text')

# by link text
element = browser.find(link_text='some link text')

# by partial link text
element = browser.find(partial_link_text='some link')

# by css selector
element = browser.find(css='.someClass')

# by xpath
element = browser.find(xpath="//input[@id='someId']")

# by tag name
element = browser.find(tag_name='input')
```


### golem.browser.**get_browser()**

Returns the browser instance. If there's none, it will open a new browser. 

The opened browser (a Selenium Webdriver object) has two extra methods: *find()* and *find_all()*. 

It is not required to explicitly open the browser, any golem action that requires a browser will open one if it is not already open and store it in *golem.execution.browser*.


### golem.browser.**activate_browser(browser_id)**

When working with multiple browsers at the same time. Use this method to activate one of the browser instances before interacting with it.

Example:

```
def some_func():
    # open two browsers, the first is active by default
    browser.open_browser('browser_one')
    browser.open_browser('browser_two')
    
    # navigate to a url using the first browser
    browser.get_browser().navigate('https:...')
    
    # activate the second browser 
    browser.activate_browser('browser_two')
    
    # navigate to a url using the second browser
    browser.get_browser().navigate('https:...')
``` 


### golem.browser.**element()**

It is equivalent to *golem.browser.get_browser().find()*

```
from golem.browser import element
from golem.actions import click

element = element(id="someId")
print(element.text)
click(element)
```

### golem.browser.**elements()**

It is equivalent to *golem.browser.get_browser().find_all()*

```
from golem.browser import elements

movies = elements(css='span.movie-title')
for movie in movies:
    print(movie.text)
```

<br>

## golem.execution

This module contains all the required values for a single test execution. This values can be accessed from anywhere and be modified if needed.
The values are:


- **browser**: the current browser instance, if it was already instantiated
- **steps**: a list of steps gathered throughout the execution. The steps end up in the report
- **browser_name**: the name of the browser selected for this single execution
- **settings**: a dictionary of settings
- **project**: the name of the current project
- **workspace**: the root working directory
- **data**: the data of the current test execution
- **report_directory**: the directory where the report will be created
- **description**: the description of the current test
- **logger**: the logger of the current execution


Next, go to [Managing Environments](environments.html)