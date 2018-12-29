WebDriver class
==================================================

## class GolemExtendedDriver()

This class represents a browser.
It extends selenium.webdriver.remote.webdriver.WebDriver.

### Methods and Properties

#### **accept_alert**(ignore_not_present=False) <small>[Golem]</small>

Accepts alert. 

Args:

* ignore_not_present: ignore NoAlertPresentException

#### **add_cookie**(cookie_dict) <small>[Selenium]</small>

Adds a cookie to your current session.

Args:
	
* cookie_dict: A dictionary object, with required keys - “name” and “value”;
optional keys - “path”, “domain”, “secure”, “expiry”

Usage:
```python
driver.add_cookie({'name': 'foo', 'value': 'bar'})
driver.add_cookie({'name': 'foo', 'value': 'bar', 'path': '/'})
driver.add_cookie({'name': 'foo', 'value': 'bar', 'path': '/', 'secure': True})
```

#### **alert_is_present**() <small>[Golem]</small>

Returns whether an alert is present

#### **application_cache** <small>[Selenium]</small>

Returns a ApplicationCache Object to interact with the browser app cache

#### **back**() <small>[Selenium]</small>

Goes one step backward in the browser history.

Usage:	driver.back()

#### **check_element**(element) <small>[Golem]</small>
Check an element (checkbox or radiobutton). If element is already checked this is ignored.

Args:

* element: an element tuple, a CSS string or a WebElement object

#### **close**() <small>[Selenium]</small>

Closes the current window.

Usage:

driver.close()

#### **close_window_by_index**(index) <small>[Golem]</small>

Close window/tab by index. Note: “The order in which the window handles are returned is arbitrary.”

Args:

* index: index of the window to close from window_handles
         
#### **close_window_by_partial_title**(partial_title) <small>[Golem]</small>

Close window/tab by partial title

#### **close_window_by_partial_url**(partial_url) <small>[Golem]</small>

Close window/tab by partial url

#### **close_window_by_title**(title) <small>[Golem]</small>

Close window/tab by title

#### **close_window_by_url**(url) <small>[Golem]</small>

Close window/tab by URL

#### **close_window_switch_back**(close_handle) <small>[Golem]</small>

Close a window/tab by handle and switch back to current handle.
If current handle is the same as close_handle, try to switch to the first available window/tab.

#### **create_web_element**(element_id) <small>[Selenium]</small>

Creates a web element with the specified element_id.

#### **current_url** <small>[Selenium]</small>

Gets the URL of the current page.

Usage:	driver.current_url

#### **current_window_handle** <small>[Selenium]</small>

Returns the handle of the current window.

Usage:

driver.current_window_handle

#### **delete_all_cookies**() <small>[Selenium]</small>

Delete all cookies in the scope of the session.

Usage:

driver.delete_all_cookies()

#### **delete_cookie**(name) <small>[Selenium]</small>

Deletes a single cookie with the given name.

Usage:

driver.delete_cookie(‘my_cookie’)

#### **desired_capabilities** <small>[Selenium]</small>

returns the drivers current desired capabilities being used

#### **dismiss_alert**(ignore_not_present=False) <small>[Golem]</small>

Dismiss alert.

Args:

* ignore_not_present: ignore NoAlertPresentException

#### **element_is_present**(element) <small>[Golem]</small>

If element is present, return the element. If element is not present return False

Args:

* element: an element tuple, a CSS string or a WebElement object

#### **execute**(driver_command, params=None) <small>[Selenium]</small>

Sends a command to be executed by a command.CommandExecutor.

Args:	

* driver_command: The name of the command to execute as a string.
* params: A dictionary of named parameters to send with the command.

Returns:	

The command’s JSON response loaded into a dictionary object.

#### **execute_async_script**(script, *args) <small>[Selenium]</small>

Asynchronously Executes JavaScript in the current window/frame.

Args:

* script: The JavaScript to execute.
* args: Any applicable arguments for your JavaScript.

Usage:	
```python
script = ("var callback = arguments[arguments.length - 1];"
          "window.setTimeout(function(){ callback('timeout') }, 3000);")
driver.execute_async_script(script)
```

#### **execute_script**(script, *args) <small>[Selenium]</small>

Synchronously Executes JavaScript in the current window/frame.

Args:	

* script: The JavaScript to execute.
* args: Any applicable arguments for your JavaScript.

Usage:	

driver.execute_script(‘return document.title;’)

#### **file_detector_context**(file_detector_class, *args, **kwargs) <small>[Selenium]</small>

Overrides the current file detector (if necessary) in limited context. Ensures the original file detector is set afterwards.

Example:
```python
with webdriver.file_detector_context(UselessFileDetector):
someinput.send_keys(‘/etc/hosts’)
```

Args:	
* file_detector_class - Class of the desired file detector. If the class is different
from the current file_detector, then the class is instantiated with args and kwargs and used as a file detector during the duration of the context manager.
* args - Optional arguments that get passed to the file detector class during
instantiation.
* kwargs - Keyword arguments, passed the same way as args.

#### **find**(*args, **kwargs) <small>[Golem]</small>

Find a WebElement

Search criteria:
* The first argument must be: an element tuple, a CSS string or a WebElement object.
* Keyword search criteria: id, name, link_text, partial_link_text, css, xpath, tag_name.
* Only one search criteria should be provided.

Other args:
* timeout: timeout (in seconds) to wait for element to be present. by default it uses the *search_timeout* setting value
* wait_displayed: wait for element to be displayed (visible). By default uses the *wait_displayed* setting value

Usage:
```python
driver.find('div#someId > input.class')
driver.find(('id', 'someId'))
driver.find(id='someId')
driver.find(xpath='//div/input', timeout=5, wait_displayed=True)
```

Returns:

A golem.webdriver.extended_webelement.ExtendedRemoteWebElement

Described in more detail [here](../finding-elements.html#find).

#### **find_all**(*args, **kwargs) <small>[Golem]</small>

Find all WebElements that match the search criteria.

Search criteria:
* The first argument must be: an element tuple, a CSS string or a WebElement object.
* Keyword search criteria: id, name, link_text, partial_link_text, css, xpath, tag_name
* Only one search criteria should be provided.

Usage:
```python
driver.find_all('div#someId > span.class')
driver.find(('tag_name', 'input'))
driver.find(xpath='//div/input')
````

Returns
    a list of ExtendedRemoteWebElement

Described in more detail [here](../finding-elements.html#find-all).

#### **find_element**(by='id', value=None) <small>[Selenium]</small>

Use [find](#find-args-kwargs-small-golem-small) instead.


#### **find_element_by_class_name**(name) <small>[Selenium]</small>

Finds an element by class name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_css_selector**(css_selector) <small>[Selenium]</small>

Finds an element by css selector.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_id**(id_) <small>[Selenium]</small>

Finds an element by id.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_link_text**(link_text) <small>[Selenium]</small>

Finds an element by link text.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_name**(name) <small>[Selenium]</small>

Finds an element by name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_partial_link_text**(link_text) <small>[Selenium]</small>

Finds an element by a partial match of its link text.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_tag_name**(name) <small>[Selenium]</small>

Finds an element by tag name.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_element_by_xpath**(xpath) <small>[Selenium]</small>

Finds an element by xpath.

Use [find](#find-args-kwargs-small-golem-small) instead.

#### **find_elements**(by='id', value=None) <small>[Selenium]</small>

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_class_name**(name) <small>[Selenium]</small>

Finds elements by class name.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_css_selector**(css_selector) <small>[Selenium]</small>

Finds elements by css selector.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_id**(id_) <small>[Selenium]</small>

Finds multiple elements by id.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_link_text**(text) <small>[Selenium]</small>

Finds elements by link text.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_name**(name) <small>[Selenium]</small>

Finds elements by name.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_partial_link_text**(link_text) <small>[Selenium]</small>

Finds elements by a partial match of their link text.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_tag_name**(name) <small>[Selenium]</small>

Finds elements by tag name.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **find_elements_by_xpath**(xpath) <small>[Selenium]</small>

Finds multiple elements by xpath.

Use [find_all](#find-all-args-kwargs-small-golem-small) instead.

#### **forward**() <small>[Selenium]</small>

Goes one step forward in the browser history.

Usage:

driver.forward()

#### **fullscreen_window**() <small>[Selenium]</small>

Invokes the window manager-specific ‘full screen’ operation

#### **get**(url) <small>[Selenium]</small>

Loads a web page in the current browser session.

#### **get_cookie**(name) <small>[Selenium]</small>

Get a single cookie by name. Returns the cookie if found, None if not.

Usage:

driver.get_cookie(‘my_cookie’)

#### **get_cookies**() <small>[Selenium]</small>

Returns a set of dictionaries, corresponding to cookies visible in the current session.

Usage:

driver.get_cookies()

#### **get_log**(log_type) <small>[Selenium]</small>

Gets the log for a given log type

Args:	
* log_type: type of log that which will be returned

Usage:	

driver.get_log(‘browser’) driver.get_log(‘driver’) driver.get_log(‘client’) driver.get_log(‘server’)

#### **get_screenshot_as_base64**() <small>[Selenium]</small>
Gets the screenshot of the current window as a base64 encoded string which is useful in embedded images in HTML.

Usage:

driver.get_screenshot_as_base64()

#### **get_screenshot_as_file**(filename) <small>[Selenium]</small>

Saves a screenshot of the current window to a PNG image file.
Returns False if there is any IOError, else returns True. Use full paths in your filename.

Args:	

* filename: The full path you wish to save your screenshot to. This should end with a .png extension.

Usage:	

driver.get_screenshot_as_file(‘/Screenshots/foo.png’)

#### **get_screenshot_as_png**() <small>[Selenium]</small>

Gets the screenshot of the current window as a binary data.

Usage:

driver.get_screenshot_as_png()

#### **get_window_index**() <small>[Golem]</small>

Get the index of the current window/tab

#### **get_window_position**(windowHandle='current') <small>[Golem]</small>

Gets the x,y position of the current window.

Usage:	driver.get_window_position()

#### **get_window_rect**() <small>[Selenium]</small>

Gets the x, y coordinates of the window as well as height and width of the current window.

Usage:	driver.get_window_rect()

#### **get_window_size**(windowHandle='current') <small>[Selenium]</small>

Gets the width and height of the current window.

Usage:	driver.get_window_size()

#### **get_window_titles**() <small>[Golem]</small>

Return a list of the titles of all open windows/tabs

#### **get_window_urls**() <small>[Golem]</small>

Return a list of the URLs of all open windows/tabs

#### **implicitly_wait**(time_to_wait) <small>[Selenium]</small>

Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.
This method only needs to be called one time per session.
To set the timeout for calls to execute_async_script, see set_script_timeout.

Args:	
* time_to_wait: Amount of time to wait (in seconds)

Usage:	

driver.implicitly_wait(30)

Use [search_timeout](../settings.html#settings) setting instead.

#### **log_types** <small>[Selenium]</small>

Gets a list of the available log types

Usage:	driver.log_types

#### **maximize_window**() <small>[Selenium]</small>

Maximizes the current window that webdriver is using

#### **minimize_window**() <small>[Selenium]</small>

Invokes the window manager-specific ‘minimize’ operation

#### **name** <small>[Selenium]</small>

Returns the name of the underlying browser for this instance.

#### **orientation** <small>[Selenium]</small>

Gets the current orientation of the device

#### **page_source** <small>[Selenium]</small>

Gets the source of the current page.

#### **quit**() <small>[Selenium]</small>

Quits the driver and closes every associated window.

#### **refresh**() <small>[Selenium]</small>

Refreshes the current page.

#### **save_screenshot**(filename) <small>[Selenium]</small>

Saves a screenshot of the current window to a PNG image file.
Returns False if there is any IOError, else returns True. Use full paths in your filename.

Args:	
* filename: The full path you wish to save your screenshot to. This should end with a .png extension.

Usage:	

driver.save_screenshot(‘/Screenshots/foo.png’)

#### **set_page_load_timeout**(time_to_wait) <small>[Selenium]</small>

Set the amount of time to wait for a page load to complete before throwing an error.

Args:	
* time_to_wait: The amount of time to wait

Usage:	

driver.set_page_load_timeout(30)

#### **set_script_timeout**(time_to_wait) <small>[Selenium]</small>

Set the amount of time that the script should wait during an execute_async_script call before throwing an error.

Args:	
*time_to_wait: The amount of time to wait (in seconds)

Usage:	

driver.set_script_timeout(30)

#### **set_window_position**(x, y, windowHandle='current') <small>[Selenium]</small>

Sets the x,y position of the current window. (window.moveTo)

Args:	
* x: the x-coordinate in pixels to set the window position
* y: the y-coordinate in pixels to set the window position

Usage:	

driver.set_window_position(0,0)

#### **set_window_rect**(x=None, y=None, width=None, height=None) <small>[Selenium]</small>

Sets the x, y coordinates of the window as well as height and width of the current window.

Usage:
```python
driver.set_window_rect(x=10, y=10)
driver.set_window_rect(width=100, height=200)
driver.set_window_rect(x=10, y=10, width=100, height=200)
```

#### **set_window_size**(width, height, windowHandle='current') <small>[Selenium]</small>

Sets the width and height of the current window. (window.resizeTo)

Args:	
*width: the width in pixels to set the window to
*height: the height in pixels to set the window to

Usage:	

driver.set_window_size(800,600)

#### **start_client**() <small>[Selenium]</small>

Called before starting a new session. This method may be overridden to define custom startup behavior.

#### **start_session**(capabilities, browser_profile=None) <small>[Selenium]</small>

Creates a new session with the desired capabilities.

Args:	
* browser_name - The name of the browser to request.
* version - Which browser version to request.
* platform - Which platform to request the browser on.
* javascript_enabled - Whether the new session should support JavaScript.
* browser_profile - A selenium.webdriver.firefox.firefox_profile.FirefoxProfile object. Only used if Firefox is requested.

#### **stop_client**() <small>[Selenium]</small>

Called after executing a quit command. This method may be overridden to define custom shutdown behavior.

#### **switch_to** <small>[Selenium]</small>

Returns:	

SwitchTo: an object containing all options to switch focus into

Usage:	
```python
element = driver.switch_to.active_element
alert = driver.switch_to.alert
driver.switch_to.default_content()
driver.switch_to.frame('frame_name')
driver.switch_to.frame(1)
driver.switch_to.frame(driver.find_elements_by_tag_name('iframe')[0])
driver.switch_to.parent_frame()
driver.switch_to.window('main')
```

#### **switch_to_active_element**() <small>[Selenium]</small>

Deprecated use driver.switch_to.active_element

#### **switch_to_alert**() <small>[Selenium]</small>

Deprecated use driver.switch_to.alert

#### **switch_to_default_content**() <small>[Selenium]</small>

Deprecated use driver.switch_to.default_content

#### **switch_to_first_window**() <small>[Golem]</small>

Switch to first window/tab

#### **switch_to_frame**(frame_reference) <small>[Selenium]</small>

Deprecated use driver.switch_to.frame

#### **switch_to_last_window**() <small>[Golem]</small>

Switch to last window/tab

#### **switch_to_next_window**() <small>[Golem]</small>

Switch to next window/tab in the list of window handles.
If current window is the last in the list this will circle back from the start.

#### **switch_to_previous_window**() <small>[Golem]</small>

Switch to previous window/tab in the list of window handles.
If current window is the first in the list this will circle back from the top.

#### **switch_to_window**(window_name) <small>[Selenium]</small>

Deprecated use driver.switch_to.window

#### **switch_to_window_by_index**(index) <small>[Golem]</small>

Switch to window/tab by index. Note: “The order in which the window handles are returned is arbitrary.”

#### **switch_to_window_by_partial_title**(partial_title) <small>[Golem]</small>

Switch to window/tab by partial title

####  **switch_to_window_by_partial_url**(partial_url) <small>[Golem]</small>

Switch to window/tab by partial URL

#### **switch_to_window_by_title**(title) <small>[Golem]</small>

Switch to window/tab by title

#### **switch_to_window_by_url**(url) <small>[Golem]</small>

Switch to window/tab by URL

#### **title** <small>[Selenium]</small>

Returns the title of the current page.

Usage:	title = driver.title

#### **uncheck_element(element)** <small>[Golem]</small>

Uncheck a checkbox element.
If element is already unchecked this is ignored.

Args
* element: an element tuple, a CSS string or a WebElement object
        
#### **wait_for_alert_present**(timeout) <small>[Golem]</small>

Wait for an alert to be present

Args:
* timeout: time to wait (in seconds)

#### **wait_for_element_displayed**(element, timeout) <small>[Golem]</small>

Wait for element to be present and displayed

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)
        
#### **wait_for_element_enabled**(element, timeout) <small>[Golem]</small>

Wait for element to be enabled

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)
        
#### **wait_for_element_has_attribute**(element, attribute, timeout) <small>[Golem]</small>

Wait for element to have attribute

Args:
* element: an element tuple, a CSS string or a WebElement object
* attribute: attribute name
* timeout: time to wait (in seconds)

Usage:

driver.wait_for_element_has_attribute('#someId', 'onclick', 5)

#### **wait_for_element_has_not_attribute**(element, attribute, timeout) <small>[Golem]</small>

Wait for element to not have attribute

Args:
* element: an element tuple, a CSS string or a WebElement object
* attribute: attribute name
* timeout: time to wait (in seconds)

Usage:
driver.wait_for_element_has_not_attribute('#someId', 'onclick', 5)
   
#### **wait_for_element_not_displayed**(element, timeout) <small>[Golem]</small>

Wait for element to be not displayed.
When element is not displayed this is ignored.
When element is not present this will raise ElementNotFound.

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)

#### **wait_for_element_not_enabled**(element, timeout) <small>[Golem]</small>

Wait for element to be not enabled

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)

#### **wait_for_element_not_present**(element, timeout) <small>[Golem]</small>

Wait for element not present in the DOM

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)

#### **wait_for_element_present**(element, timeout) <small>[Golem]</small>

Wait for element present in the DOM

Args:
* element: an element tuple, a CSS string or a WebElement object
* timeout: time to wait (in seconds)

#### **wait_for_element_text**(element, text, timeout) <small>[Golem]</small>

Wait for element text to match given text

Args:
* element: an element tuple, a CSS string or a WebElement object
* text: expected element text to be
* timeout: time to wait (in seconds)

#### **wait_for_element_text_contains**(element, text, timeout) <small>[Golem]</small>

Wait for element to contain text

Args:
* element: an element tuple, a CSS string or a WebElement object
* text: expected element to be contained by element
* timeout: time to wait (in seconds)

#### **wait_for_element_text_is_not**(element, text, timeout) <small>[Golem]</small>

Wait for element text to not match given text

Args:
* element: an element tuple, a CSS string or a WebElement object
* text: expected text to not be element's text
* timeout: time to wait (in seconds)

#### **wait_for_element_text_not_contains**(element, text, timeout) <small>[Golem]</small>

Wait for element to not contain text

Args:
* element: an element tuple, a CSS string or a WebElement object
* text: expected text to not be contained in element
* timeout: time to wait (in seconds)

#### **wait_for_page_contains_text**(text, timeout) <small>[Golem]</small>

Wait for page to contains text

Args:
* text: text to be contained in page source
* timeout: time to wait (in seconds)

#### **wait_for_page_not_contains_text**(text, timeout) <small>[Golem]</small>

Wait for page to not contain text

Args:
* text: text to not be contained in page source
* timeout: time to wait (in seconds)

#### **wait_for_title**(title, timeout) <small>[Golem]</small>

Wait for page title to be the given value

Args:
* title: expected title
* timeout: time to wait (in seconds)

#### **wait_for_title_contains**(partial_title, timeout) <small>[Golem]</small>

Wait for page title to contain partial_title

Args:
* partial_title: expected partial title
* timeout: time to wait (in seconds)

#### **wait_for_title_is_not**(title, timeout) <small>[Golem]</small>

Wait for page title to not be the given value

Args:
* title: not expected title
* timeout: time to wait (in seconds)

#### **wait_for_title_not_contains**(partial_title, timeout) <small>[Golem]</small>

Wait for page title to not contain partial_title

Args:
* partial_title: not expected partial title
* timeout: time to wait (in seconds)

#### **wait_for_window_present_by_partial_title**(partial_title, timeout) <small>[Golem]</small>

Wait for window/tab present by partial title

#### **wait_for_window_present_by_partial_url**(partial_url, timeout) <small>[Golem]</small>

Wait for window/tab present by partial url

#### **wait_for_window_present_by_title**(title, timeout) <small>[Golem]</small>

Wait for window/tab present by title

#### **wait_for_window_present_by_url**(url, timeout) <small>[Golem]</small>

Wait for window/tab present by url

#### **window_handles** <small>[Selenium]</small>

Returns the handles of all windows within the current session.

Usage:	driver.window_handles
