WebElement class
==================================================

## class ExtendedWebElement()

This class represents a web element.
It extends selenium.webdriver.remote.webelement.WebElement.

### Methods and Properties

#### **check**() <small>[Golem]</small>

Check element if element is checkbox or radiobutton.
If element is already checked, this is ignored.

#### **clear**() <small>[Selenium]</small>

Clears the text if it’s a text entry element.

#### **click**() <small>[Selenium]</small>
Clicks the element.

#### **double_click**() <small>[Golem]</small>
Double click the element

#### **find**(*args, **kwargs) <small>[Golem]</small>
Find a WebElement

Search criteria:
* The first argument must be: an element tuple, a CSS string or a WebElement object.
* Keyword search criteria: id, name, link_text, partial_link_text, css, xpath, tag_name.
* Only one search criteria should be provided.

Other args:
* timeout: timeout (in seconds) to wait for element to be present. By default it uses the search_timeout setting value.
* wait_displayed: wait for element to be displayed (visible). By default uses the wait_displayed setting value.

Usage:
```python
element.find('div#someId > input.class')
element.find(('id', 'someId'))
element.find(id='someId')
element.find(xpath='//div/input', timeout=5, wait_displayed=True)
```

Returns: a golem.webdriver.extended_webelement.ExtendedRemoteWebElement

#### **find_all**(*args, **kwargs) <small>[Golem]</small>

Find all WebElements that match the search criteria.

Search criteria:
* The first argument must be: an element tuple, a CSS string or a WebElement object.
* Keyword search criteria: id, name, link_text, partial_link_text, css, xpath, tag_name.
* Only one search criteria should be provided.

Usage:
```python
element.find_all('div#someId > span.class')
element.find(('tag_name', 'input'))
element.find(xpath='//div/input')
```

Returns: a list of ExtendedRemoteWebElement

#### **find_element**(by='id', value=None) <small>[Selenium]</small>

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_class_name**(name) <small>[Selenium]</small>

Finds element within this element’s children by class name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_css_selector**(css_selector) <small>[Selenium]</small>

Finds element within this element’s children by CSS selector.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_id**(id_) <small>[Selenium]</small>

Finds element within this element’s children by ID.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_link_text**(link_text) <small>[Selenium]</small>

Finds element within this element’s children by visible link text.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_name**(name) <small>[Selenium]</small>

Finds element within this element’s children by name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_partial_link_text**(link_text) <small>[Selenium]</small>

Finds element within this element’s children by partially visible link text.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_tag_name**(name) <small>[Selenium]</small>

Finds element within this element’s children by tag name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_xpath**(xpath) <small>[Selenium]</small>

Finds element by xpath.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_elements**(by='id', value=None) <small>[Selenium]</small>

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_css_selector**(css_selector) <small>[Selenium]</small>

Finds a list of elements within this element’s children by CSS selector.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_id**(id_) <small>[Selenium]</small>

Finds a list of elements within this element’s children by ID. Will return a list of webelements if found, or an empty list if not.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_link_text**(link_text) <small>[Selenium]</small>

Finds a list of elements within this element’s children by visible link text.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_name**(name) <small>[Selenium]</small>

Finds a list of elements within this element’s children by name.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_partial_link_text**(link_text) <small>[Selenium]</small>

Finds a list of elements within this element’s children by link text.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_tag_name**(name) <small>[Selenium]</small>

Finds a list of elements within this element’s children by tag name.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_xpath**(xpath) <small>[Selenium]</small>

Finds elements within the element by xpath.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **focus**() <small>[Golem]</small>

Give focus to element

#### **get_attribute**(name) <small>[Selenium]</small>

Gets the given attribute or property of the element.

This method will first try to return the value of a property with the given name.
If a property with that name doesn’t exist, it returns the value of the attribute with the same name.
If there’s no attribute with that name, None is returned.

Values which are considered truthy, that is equals “true” or “false”, are returned as booleans.
All other non-None values are returned as strings.
For attributes or properties which do not exist, None is returned.

Args:	
* name - Name of the attribute/property to retrieve.

Example:
```python
# Check if the "active" CSS class is applied to an element.
is_active = "active" in target_element.get_attribute("class")
```

#### **get_property**(name) <small>[Selenium]</small>
Gets the given property of the element.

Args:	
* name - Name of the property to retrieve.

Example:
```python
text_length = target_element.get_property("text_length")
```

#### **has_attribute**(attribute) <small>[Golem]</small>

Returns whether element has attribute

#### **has_focus**() <small>[Golem]</small>

Returns whether element has focus

#### **id** <small>[Selenium]</small>

Internal ID used by selenium.

This is mainly for internal use.
Simple use cases such as checking if 2 webelements refer to the same element, can be done using ==:

```python
if element1 == element2:
    print("These 2 are equal")
```

#### **inner_html** <small>[Golem]</small>

Element innerHTML attribute

#### **is_displayed**() <small>[Selenium]</small>

Whether the element is visible to a user.

#### **is_enabled**() <small>[Selenium]</small>

Returns whether the element is enabled.

#### **is_selected**() <small>[Selenium]</small>

Returns whether the element is selected.

Can be used to check if a checkbox or radio button is selected.

#### **javascript_click**() <small>[Golem]</small>

Click element using Javascript

#### **location** <small>[Selenium]</small>

The location of the element in the renderable canvas.

#### **location_once_scrolled_into_view** <small>[Selenium]</small>

THIS PROPERTY MAY CHANGE WITHOUT WARNING.
Use this to discover where on the screen an element is so that we can click it.
This method should cause the element to be scrolled into view.

Returns the top lefthand corner location on the screen, or None if the element is not visible.

#### **mouse_over**() <small>[Golem]</small>

Mouse over element

#### **outer_html** <small>[Golem]</small>

Element outerHTML attribute

#### **parent** <small>[Selenium]</small>

Internal reference to the WebDriver instance this element was found from.

#### **press_key**(key) <small>[Golem]</small>

Press a key on element

Usage:
```python
element.press_key('ENTER')
element.press_key('TAB')
element.press_key('LEFT')
```

#### **rect** <small>[Selenium]</small>

A dictionary with the size and location of the element.

#### **screenshot**(filename) <small>[Selenium]</small>

Saves a screenshot of the current element to a PNG image file.
Returns False if there is any IOError, else returns True. Use full paths in your filename.

Args:	
* filename: The full path you wish to save your screenshot to. This should end with a .png extension.

Usage: element.screenshot(‘/Screenshots/foo.png’)

#### **screenshot_as_base64** <small>[Selenium]</small>

Gets the screenshot of the current element as a base64 encoded string.

Usage:	img_b64 = element.screenshot_as_base64

#### **screenshot_as_png** <small>[Selenium]</small>

Gets the screenshot of the current element as a binary data.

Usage: element_png = element.screenshot_as_png

#### **select** <small>[Golem]</small>

Return a Select object

#### **send_keys**(*value) <small>[Selenium]</small>

Simulates typing into the element.

Args:	
* value - A string for typing, or setting form fields.
For setting file inputs, this could be a local file path.
Use this to send simple key events or to fill out form fields:
```python
form_textfield = driver.find_element_by_name('username')
form_textfield.send_keys("admin")
```

This can also be used to set file inputs.
```python
file_input = driver.find_element_by_name('profilePic')
file_input.send_keys("path/to/profilepic.gif")
# Generally it's better to wrap the file path in one of the methods
# in os.path to return the actual path to support cross OS testing.
# file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))
```

#### **send_keys_with_delay**(value, delay=0.1) <small>[Golem]</small>

Send keys to element one by one with a delay between keys.

Args:
 - value: a string to type
 - delay: time between keys (in seconds)

Raises:
 - ValueError: if delay is not a positive int or float

#### **size** <small>[Selenium]</small>

The size of the element.

#### **submit**() <small>[Selenium]</small>

Submits a form.

#### **tag_name** <small>[Selenium]</small>
This element’s tagName property.

#### **text** <small>[Selenium]</small>

The text of the element.

#### **uncheck**() <small>[Golem]</small>

Uncheck element if element is checkbox. If element is already unchecked, this is ignored.

#### **value** <small>[Golem]</small>

The value attribute of element

#### **value_of_css_property**(property_name) <small>[Selenium]</small>

The value of a CSS property.

#### **wait_displayed**(timeout=30) <small>[Golem]</small>

Wait for element to be displayed

Returns: The element

#### **wait_enabled**(timeout=30) <small>[Golem]</small>

Wait for element to be enabled

Returns: The element

#### **wait_has_attribute**(attribute, timeout=30) <small>[Golem]</small>

Wait for element to have attribute

Returns: The element

#### **wait_has_not_attribute**(attribute, timeout=30) <small>[Golem]</small>

Wait for element to not have attribute

Returns: The element

#### **wait_not_displayed**(timeout=30) <small>[Golem]</small>

Wait for element to be not displayed

Returns: The element

#### **wait_not_enabled**(timeout=30) <small>[Golem]</small>

Wait for element to be not enabled

Returns: The element

#### **wait_text**(text, timeout=30) <small>[Golem]</small>

Wait for element text to match given text

Returns: The element

#### **wait_text_contains**(text, timeout=30) <small>[Golem]</small>

Wait for element to contain given text

Returns: The element

#### **wait_text_is_not**(text, timeout=30) <small>[Golem]</small>

Wait fo element text to not match given text

Returns: The element

#### **wait_text_not_contains**(text, timeout=30) <small>[Golem]</small>

Wait for element text to not contain text

Returns: The element

