Tutorial - Part 2
==================================================


## Adding a New Test File

**Test files** are Python modules located inside the *tests* folder of a project.

To create a new **test file** use the following command:

```
golem createtest <project_name> <test_name>
```

A test can also be created from the Web Module.

### A test example

Next is a test that navigates to 'en.wikipedia.org', searches an article and validates that the title of the article is correct.

**validate_article_title.py**
```python

description = 'Search an article in Wikipedia'

def test_validate_article_title(data):
    navigate('http://en.wikipedia.org/')
    send_keys(('id', 'searchInput'), 'automation')
    click(('id', 'searchButton'))
    verify_element_text(('id', 'firstHeading'), 'Automation')
```

In the Web Module:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/test_example.jpg)

### Golem Actions

In the previous example, *navigate*, *send_keys*, *click*, and *verify_element_text* are Golem actions. Check out [the entire list of actions](golem-actions.html).


### Opening and Closing the Browser

There is no need to open or close the browser.
The first action that requires a browser will open one. At the end, Golem will close the browser.
However, this can be done explicitly with the [open_browser](golem-actions.html#open-browser-browser-id-none) and [close_browser](golem-actions.html#close-browser) actions.

## Running a Test

To run the test just press the 'Run Test' button in the Web Module or run the following command:

```
golem run <project_name> validate_article_title
```


## Managing Test Data

The data for each test can be stored inside the test file, in CSV or JSON files.

### Using the CSV Data Table

Let's rewrite the previous test but extracting all the data outside the code:

In the Test Builder select *Add Data Source* -> *CSV*.
Then we fill the table with the following values:

**validate_article_title.csv**
```
URL,search_value,article_title
http://en.wikipedia.org/,automation,Automation
```

And we refactor the test to use the data object instead of hardcoded values:

**validate_article_title.py**
```python
description = 'Search an article in Wikipedia'

def test_validate_article_title(data):
    go_to(data.URL)
    send_keys(('id', 'searchInput'), data.search_value)
    click(('id', 'searchButton'))
    verify_element_text(('id', 'firstHeading'), data.article_title)
```

This is the final result:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/test_example_with_datatable.jpg)


### Multiple data sets

The test will be executed once per each row in the CSV file. Each row is considered a **data set**.

For example, consider the previous data file, but with more rows:

**validate_article_title.csv**
```text
URL,search_value,article_title
http://en.wikipedia.org/,automation,Automation
http://en.wikipedia.org/,webdriver,Selenium (software)
http://es.wikipedia.org/,chimichanga,Chimichanga
http://fr.wikipedia.org/,soupe à l'oignon,Soupe à l'oignon
```

Using this data file, Golem will run the same test 4 times, using each time a different data set.

Test data can also be [JSON](test-data.html#json-data) and [internal](test-data.html#internal-data).


## Using Page Objects

If you remember from the previous example, each time the test interacted with a web element (an HTML tag), the selector for that element was defined right there inside the step. That will make the tests hard to maintain, especially when the application under test changes.


### Defining Page Objects

It is a good practice to keep the selectors of the web elements outside of the test, and declared once in a single place.
That place should be a **Page Object**.

A Page Object represents an entire page of the application (or a part of a page, like the header or the menu).
Inside the Page Object, the elements of the page can be defined so they can be used later in the tests. 

Let's see an example. Consider the previous test (validate_article_title).
Let's extract all the element selectors and put them inside Page Objects.

For this, we create two pages. The first will be the 'header', as it's the same header for every page of the application.
The second page object will be the 'article'.

**header.py**
```python
search_input = ('id', 'searchInput')

search_button = ('id', 'searchButton')
```

**article.py**
```python
title = ('id', 'firstHeading')
```

These pages, as seen with the Web Module, look like this:

<img class="border-image" src="https://raw.githubusercontent.com/golemhq/resources/master/img/page_example_header.jpg">

<br>

<img class="border-image" src="https://raw.githubusercontent.com/golemhq/resources/master/img/page_example_article.jpg">


### Using Pages Inside Tests

Having these two pages created, we can use them in our test, and refactor it as follows:

**validate_article_title.py**
```python
description = 'Search an article in Wikipedia'

pages = ['header', 'article']

def test_validate_article_title(data):
    navigate(data.URL)
    send_keys(header.search_input, data.search_value)
    click(header.search_button)
    verify_element_text(article.title, data.article_title)
```

In the Web Module:

![](https://raw.githubusercontent.com/golemhq/resources/master/img/test_example_with_datatable_and_pages.jpg)

With this change, the 'Search input', 'Search button' and 'Article Title' elements are defined in a separate file.
A test that needs to interact with these elements, just needs to import the page object and reference them.
This reduces the required time to write new tests and the maintenance of existing tests.

## Creating a suite

A suite lets you arbitrarily select a subset of all the tests to execute as a group.

A suite contains a list of *tests*, *browsers*, *environments*, *tags*, and the number of *processes*.
Consider the following example:

**full_regression.py**
```python

browsers = ['chrome', 'firefox']

environments = ['staging']

processes = 3

tags = []

tests = [
    'module.module_test1',
    'module.module_test2',
    'another_test',
    'validate_article_title'
]
```

<img class="border-image" src="https://raw.githubusercontent.com/golemhq/resources/master/img/suite_example.jpg">

<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>This suite will execute all marked tests, once per each browser, environment and test set</p>
</div>


### Test Parallelization

The ```processes = 2``` tells Golem how many tests should be executed at the same time. The default is one (one at a time).
How many tests can be parallelized depends on your test infrastructure.


### Execution report

When the suite finishes a JSON report is generated in the *reports* folder. This report can be visualized using the Web Module. 

<br>

That's it! The basic tutorial ends here.
Feel free to learn more about Golem using the table of contents.
Happy testing!
