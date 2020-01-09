Golem Actions
==================================================

Golem comes with a list of predefined actions that cover most of the scenarios for tests.
They are self-documenting, meaning, they store the steps, logs and screenshots in the execution report.

Location: golem.**actions**

**A note on assertions and verifications:**

Actions that start with 'assert_' are hard assertions.
They will stop the test when they fail (jump to teardown) and the test will end with result: failure.

Actions that start with 'verify_' are soft assertions.
When a verify_ action fails it stores an error but the test continues with the next statement.
The test will end with result: error.


## Alerts

### accept_alert(ignore_not_present=False)

Accept an alert, confirm or prompt box. Use ignore_not_present to ignore error when alert is not present.

### assert_alert_not_present()

Assert an alert is not present. This applies to alerts, confirms and prompts.

### assert_alert_present()

Assert an alert is present. This applies to alerts, confirms and prompts.

### assert_alert_text(text)

Assert alert text. This will fail if there is no alert present.

### assert_alert_text_is_not(text)

Assert alert text is not text. This will fail if there is no alert present.

### dismiss_alert(ignore_not_present=False)

Dismiss an alert, confirm or prompt box. When ignore_not_present is True the error when alert is not present is ignored.

### get_alert_text()

Get text of alert, confirm or prompt box

### send_text_to_alert(text)

Send text to an alert

### submit_prompt_alert(text)

Send text to a prompt alert and accept it. If there is no prompt alert present this will fail.

### verify_alert_is_not_present()

DEPRECATED, use verify_alert_not_present

### verify_alert_is_present()

DEPRECATED, use verify_alert_present

### verify_alert_not_present()

Verify an alert is not present. This applies to alerts, confirms and prompts.

### verify_alert_present()

Verify an alert is present. This applies to alerts, confirms and prompts.

### verify_alert_text(text)

Verify alert text. This will fail if there is no alert present.

### verify_alert_text_is_not(text)

Verify alert text is not text. This will fail if there is no alert present.

### wait_for_alert_present(timeout=30)

Wait for an alert to be present

## API

### assert_response_status_code(response, status_code)

assert response status code

### http_get(url, headers={}, params={})

Perform an HTTP GET request to the URL, with the given headers and params.
Headers and params must be Python dictionaries and are optional.
The response is stored in 'data.last_response'.
Returns the response.

Example:
```
http_get('http://google.com/')
assert_equals(data.last_response.status_code, 200)
```

### http_post(url, headers={}, data={}, verify_ssl_cert=True)

Perform an HTTP POST request to the URL, with the given headers and data.
Headers and params must be Python dictionaries and are optional.
The response is stored in 'data.last_response'
Returns the response.

### verify_response_status_code(response, status_code)

Verify response status code

## Browser

### activate_browser(browser_id)

Activates a browser to use in subsequent actions.
When opening more than one browser (not windows or tabs) for a single test, the new browser can be assigned to an ID.
Default browser ID is 'main'.

### close()

DEPRECATED, use close_browser or close_window instead.

### close_browser()

Closes the webdriver browser and all it's windows/tabs

### get_browser()

Returns the active browser driver object

### get_window_size()

Return the window size with the following format:
    
```
size = {
    'width': x,
    'height': y
}
```

### maximize_window()

### open_browser(browser_id=None)

Open a new browser.
browser_id is optional and only used to manage more than one browser for the same test.
Default browser ID is 'main'.

### set_window_size(width, height)

Set the width and height of the window (in pixels)

## Cookies

### add_cookie(cookie_dict)

Add a cookie to the current session.
    
Required keys are: "name" and "value". Optional keys are: "path", "domain", "secure", "expiry"

Note:
* If a cookie with the same name exists, it will be overridden.
* This function cannot set the domain of a cookie, the domain URL
must be visited by the browser first.
* The domain is set automatically to the current domain the browser is in.
* If the browser did not visit any URL (initial blank page) this
function will fail with "Message: unable to set cookie"

**Example usage:**

add_cookie({'name': 'foo', 'value': 'bar'})

### assert_cookie_present(name)

Assert a cookie exists in the current session by the cookie name

### assert_cookie_value(name, value)

Assert the value of a cookie.
This will fail if the cookie does not exist.

### delete_all_cookies()

Delete all cookies from the current session.
Note: this only deletes cookies from the current domain.

### delete_cookie(name)

Delete a cookie from the current session.

### get_cookie(name)

Get a cookie by its name.
Returns the cookie if found, None if not.

### get_cookies()

Returns a list of dictionaries, corresponding to cookies present in the current session.

### verify_cookie_exists(name)

DEPRECATED, use verify_cookie_present instead.

### verify_cookie_present(name)

Verify a cookie exists in the current session by the cookie name

### verify_cookie_value(name, value)
Verify the value of a cookie.
This will fail if the cookie does not exist.

## Element

### assert_element_attribute(element, attribute, value)

Assert value of element attribute

### assert_element_attribute_is_not(element, attribute, value)

Assert the value of attribute of element is not 'value'

### assert_element_checked(element)

Assert element is checked. This applies to checkboxes and radio buttons.

### assert_element_displayed(element)

Assert element is displayed (visible to the user)

### assert_element_enabled(element)

Assert that element is enabled

### assert_element_has_attribute(element, attribute)

Assert element has attribute

### assert_element_has_focus(element)

Assert element has focus

### assert_element_has_not_attribute(element, attribute)

Assert element does not have attribute

### assert_element_has_not_focus(element)

Assert element does not have focus

### assert_element_not_checked(element)

Assert element is not checked.
This applies to checkboxes and radio buttons.

### assert_element_not_displayed(element)

Assert element is not displayed (visible to the user)

### assert_element_not_enabled(element)

Assert that element is not enabled

### assert_element_not_present(element)

Assert element is not present in the DOM

### assert_element_present(element)

Assert element is present in the DOM

### assert_element_text(element, text)

Assert the text of the element

### assert_element_text_contains(element, text)

Assert element contains text

### assert_element_text_is_not(element, text)

Assert the text of the element is not *text*

### assert_element_text_not_contains(element, text)

Assert element does not contain *text*

### assert_element_value(element, value)

Assert element value

### assert_element_value_is_not(element, value)

Assert element value is not *value*

### check_element(element)

Check an element (checkbox or radiobutton).
If element is already checked this is is ignored.

### clear(element)

DEPRECATED, use clear_element instead

### clear_element(element)

Clear element (e.g. a text input)

### click(element)

Perform a mouse click on element

### double_click(element)

Perform a double click on element

### focus_element(element)

Give focus to element

### get_element_attribute(element, attribute)

Get the attribute value of element.
If the attribute is not present in element, None is returned.
   
### get_element_text(element)

Get the element text

### get_element_value(element)

Get the element value attribute

### javascript_click(element)

Click an element using Javascript

### mouse_hover(element)

DEPRECATED, use mouse_over instead

### mouse_over(element)

Perform a mouse over on the element

### press_key(element, key)

Press a given key in the element.
Key must be a string with a value defined in selenium.webdriver.common.keys.Keys

Examples:
```
press_key('ENTER')
press_key('TAB')
press_key('LEFT')
```

### send_secure_keys(element, text)

Send keys to element. Text is hidden from logs and report (masked by asterisks).

### send_keys(element, text)

Send text to element

### send_keys_with_delay(element, text, delay=0.1)

Send keys to element one by one with a delay between keys.
Delay must be a positive int or float.

### submit_form(element)

Submit form. Element can be the form itself or any child element.

### uncheck_element(checkbox)

Uncheck a checkbox. If element is already checked this is is ignored.

### verify_element_attribute(element, attribute, value)

Verify the value of attribute of element

### verify_element_attribute_is_not(element, attribute, value)

Verify the value of attribute of element is not *value*

### verify_element_checked(element)

Verify element is checked. This applies to checkboxes and radio buttons.

### verify_element_displayed(element)

Verify element is displayed (visible to the user)

### verify_element_enabled(element)

Verify that element is enabled

### verify_element_has_attribute(element, attribute)

Verify element has attribute

### verify_element_has_focus(element)

Verify element has focus

### verify_element_has_not_attribute(element, attribute)

Verify element does not have attribute

### verify_element_has_not_focus(element)

Verify element does not have focus

### verify_element_not_checked(element)

Verify element is not checked. This applies to checkboxes and radio buttons.

### verify_element_not_displayed(element)

Verify element is not displayed (visible to the user)

### verify_element_not_enabled(element)

Verify that element is not enabled

### verify_element_not_present(element)

Verify element is not present in the DOM

### verify_element_present(element)

Verify element is present in the DOM

### verify_element_text(element, text)

Verify the text of the element

### verify_element_text_contains(element, text)

Verify element contains text

### verify_element_text_is_not(element, text)

Verify the text of the element is not *text*

### verify_element_text_not_contains(element, text)

Verify element does not contain text

### verify_element_value(element, value)

Verify element value

### verify_element_value_is_not(element, value)

Verify element value is not *value*

### verify_exists(element)

DEPRECATED, use verify_element_present

### verify_is_enabled(element)

DEPRECATED, use verify_element_enabled

### verify_is_not_enabled(element)

DEPRECATED, use verify_element_not_enabled

### verify_is_not_selected(element)

DEPRECATED, use verify_element_not_checked

### verify_is_not_visible(element)

DEPRECATED, use verify_element_not_displayed

### verify_is_selected(element)

DEPRECATED, use verify_element_checked

### verify_is_visible(element)

DEPRECATED, use verify_element_displayed

### verify_not_exists(element)

DEPRECATED, use verify_element_not_present

### verify_text_in_element(element, text)

DEPRECATED, use verify_element_text or verify_element_text_contains

### wait_for_element_displayed(element, timeout=30)

Wait for element to be present and displayed

### wait_for_element_enabled(element, timeout=30)

Wait for element to be enabled

### wait_for_element_has_attribute(element, attribute timeout=30)

Wait for element to have attribute

### wait_for_element_has_not_attribute(element, attribute timeout=30)

Wait for element to not have attribute

### wait_for_element_not_displayed(element, timeout=30)

Wait for element to be not displayed.
When element is not displayed this is ignored.
When element is not present this will raise ElementNotFound.

### wait_for_element_not_enabled(element, timeout=30)

Wait for element to be not enabled

### wait_for_element_not_exist(element, timeout=20)

DEPRECATED, use wait_for_element_not_present

### wait_for_element_not_present(element, timeout=30)

Wait for element to stop being present in the DOM.
If element is already not present, this will be ignored.

### wait_for_element_not_visible(element, timeout=20)

DEPRECATED, use wait_for_element_not_displayed

### wait_for_element_present(element, timeout=30)

Wait for element to be present in the DOM

### wait_for_element_text(element, text, timeout=30)

Wait for element text to match given text

### wait_for_element_text_contains(element, text, timeout=30)

Wait for element text to contain given text

### wait_for_element_text_is_not(element, text, timeout=30)

Wait for element text to not match given text

### wait_for_element_text_not_contains(element, text, timeout=30)

Wait for element text to not contain given text

### wait_for_element_visible(element, timeout=20)

DEPRECATED, use wait_for_element_displayed

## Frames

### switch_to_default_content()

Switch to default content (default frame)

### switch_to_frame(frame)

Switch to frame. frame must be the index, name, or the frame webelement itself.

### switch_to_parent_frame()

Switch to the parent of the current frame

## Select

### assert_selected_option_by_text(element, text)

Assert the option selected in a \<select\> by the option text

### assert_selected_option_by_value(element, text)

Assert the option selected in a \<select\> by the option value

### select_by_index(element, text)

DEPRECATED, use select_option_by_index instead

### select_by_text(element, text)

DEPRECATED, use select_option_by_text instead

### select_by_value(element, value)

DEPRECATED, use select_option_by_value instead

### select_option_by_index(element, text)

Select an option from a \<select\> element by index (starts from 0)

### select_option_by_text(element, text)

Select an option from a \<select\> element by the option text

### select_option_by_value(element, value)

Select an option from a \<select\> element by the option value. 

For example, given:

```
<select id="countrySelect">
    <option value="CA">Canada</option>
    <option value="US">United States</option>
    <option value="MX">Mexico</option>
</select>
```

To select the first option use:

```
select_option_by_index('#countrySelect', 0)
select_option_by_text('#countrySelect', 'Canada')
select_option_by_value('#countrySelect', 'CA')
```

### verify_selected_option(element, text)

DEPRECATED, use verify_selected_option_by_text or verify_selected_option_by_value

### verify_selected_option_by_text(element, text)

Verify the option selected in a \<select\> by the option text

### verify_selected_option_by_value(element, text)

Verify the option selected in a \<select\> by the option value

## Window

### assert_page_contains_text(text)

Assert the given text is present anywhere in the page (in the entire DOM)

### assert_page_not_contains_text(text)

Assert the given text is present anywhere in the page (in the entire DOM)

### assert_title(title)

Assert the page title

### assert_title_contains(partial_title)

Assert the page title contains partial_title

### assert_title_is_not(title)

Assert the page title is not title

### assert_title_not_contains(text)

Assert the page title does not contain text

### assert_url(url)

Assert the current URL

### assert_url_contains(partial_url)

Assert the current URL contains partial_url

### assert_url_is_not(url)

Assert the current URL is not url

### assert_url_not_contains(partial_url)

Assert the current URL does not contain partial_url

### execute_javascript(script, *args)

Execute javascript code

Examples:
```python
from golem import actions

# return the title of the page
title = actions.execute_javascript('return document.title')

# pass an element and click it using Javascript
element = actions.get_browser().find('#myElement')
actions.execute_javascript('arguments[0].click()', element)
```

### get(url)

Navigate to a URL, same as *navigate(url)*

### get_active_element()

Returns the element with focus, or BODY if nothing has focus

### get_current_url()

Returns the current browser URL

### get_page_source()

Get the entire source code of the page

### get_window_title()

### go_back()

Goes one step backward in the browser history

### go_forward()

Goes one step forward in the browser history

### navigate(url)

Navigate to a URL

### refresh_page()

Refreshes the page

### verify_page_contains_text(text)

Verify the given text is present anywhere in the page (in the entire DOM)

### verify_page_not_contains_text(text)

Verify the given text is present anywhere in the page (in the entire DOM)

### verify_text(text)

DEPRECATED, use verify_page_contains_text

### verify_title(title)

Verify the page title

### verify_title_contains(partial_title)

Verify the page title contains partial_title

### verify_title_is_not(title)

Verify the page title is not *title*

### verify_title_not_contains(text)

Verify the page title does not contain *text*

### verify_url(url)

Verify the current URL

### verify_url_contains(partial_url)

Verify the current URL contains partial_url

### verify_url_is_not(url)

Verify the current URL is not url

### verify_url_not_contains(partial_url)

Verify the current URL does not contain partial_url

### wait_for_page_contains_text(text, timeout=30)

Wait for page to contain text in the DOM

### wait_for_page_not_contains_text(text, timeout=30)

Wait for page to not contain text in the DOM

### wait_for_title(title, timeout=30)

Wait for page title to be the given value

### wait_for_title_contains(partial_title, timeout=30)

Wait for page title to contain partial_title

### wait_for_title_is_not(title, timeout=30)

Wait for page title to not be the given value

### wait_for_title_not_contains(partial_title, timeout=30)

Wait for page title to not contain partial_title

## Windows / Tabs

### assert_amount_of_windows(amount)

Assert the amount of open windows/tabs

### assert_window_present_by_partial_title(title)

Assert there is a window/tab present by partial title

### assert_window_present_by_partial_url(partial_url)

Assert there is a window/tab present by partial URL

### assert_window_present_by_title(title)

Assert there is a window/tab present by title

### assert_window_present_by_url(url)

Assert there is a window/tab present by URL

### close_window()

Close current window/tab.
If there is only one window, this will close the browser, use close_browser instead.
If there are other windows open, this will switch to the first window afterwards.

### close_window_by_index()

Close window/tab by index.
Note: "The order in which the window handles are returned is arbitrary."

### close_window_by_partial_title(partial_title)

Close window/tab by partial title

### close_window_by_partial_url(partial_url)

Close window/tab by partial URL

### close_window_by_title(title)

Close window/tab by title

### close_window_by_url(url)

Close window/tab by URL

### get_window_handle()

### get_window_handles()

Return a list with the handles of all the open windows/tabs

### get_window_index()

Get the index of the current window/tab from the list of window handles

### get_window_titles()

Return a list with the titles of all the open windows/tabs

### switch_to_first_window()

Switch to first window/tab (in the list of window handles)

### switch_to_last_window()

Switch to last window/tab (in the list of window handles)

### switch_to_next_window()

Switch to next window/tab in the list of window handles.
If current window is the last in the list this will circle back from the start.

### switch_to_previous_window()

Switch to previous window/tab in the list of window handles.
If current window is the first in the list of window handles this will circle back from the top.

### switch_to_window_by_index(index)

Switch to window/tab by index.
Note: "The order in which the window handles are returned is arbitrary."

### switch_to_window_by_partial_title(partial_title)

Switch to window/tab by partial Title

### switch_to_window_by_partial_url(partial_url)

Switch to window/tab by partial URL

### switch_to_window_by_title(title)

Switch to window/tab by title

### switch_to_window_by_url(url)

Switch to window/tab by title

### verify_amount_of_windows(amount)

Verify the amount of open windows/tabs

### verify_window_present_by_partial_title(title)

Verify there is a window/tab present by partial title

### verify_window_present_by_partial_url(partial_url)

Verify there is a window/tab present by partial URL

### verify_window_present_by_title(title)

Verify there is a window/tab present by title

### verify_window_present_by_url(url)

Verify there is a window/tab present by URL

### wait_for_window_present_by_partial_title(partial_title, timeout=30)

Wait for window/tab present by partial title

### wait_for_window_present_by_partial_url(partial_url, timeout=30)

Wait for window/tab present by partial url

### wait_for_window_present_by_title(title, timeout=30)

Wait for window/tab present by title

### wait_for_window_present_by_url(url, timeout=30)

Wait for window/tab present by url

## General Actions

### assert_contains(element, value)

DEPRECATED. Assert that the element contains the value

### assert_equals(actual, expected)

DEPRECATED. Assert that the actual value equals the expected value

### assert_false(condition)

DEPRECATED. Assert that the condition is false

### assert_true(condition)

DEPRECATED. Assert that the condition is true

### capture(message='')

DEPRECATED, use take_screenshot instead.
Take a screenshot of the browser, the message is optional

### debug()

DEPRECATED, use interactive_mode instead.

### error(message='')

Add an error to the test. The test will continue.

### fail(message='')

Mark the test as failure and stop

### get_data()

Return test data.

### get_secrets()

Return the secrets object.

### get_search_timeout()

Get search timeout.

### interactive_mode()

Starts an interactive console at this point of the test.
The test should be run with the '-i' flag, otherwise this action will be ignored.
See [Interactive Mode](interactive-mode.html) for more details.

### log(message, level='INFO')

Log a message. Valid log levels are: DEBUG, INFO, WARNING, ERROR and CRITICAL.

### random(args)

DEPRECATED, use random_str, random_int or random_float. 

Generate a random string. Options:

* 'c' generate a random lowercase letter
* 'd' generate a random digit

For example: random('cccddd') => 'aeg147'


### random_float(min=1.0, max=100.0, decimals=None)

Generate a random float between min and max.
*Decimals* is the maximum amount of decimal places the generated float should have.

### random_int(min=1, max=100)

Generate a random integer between min and max

### random_str(length=10, sample=None, prefix='', suffix='')

Generate a random string.
*Sample* should be a string or a list of strings/characters to
choose from. The default sample is lowercase ascii letters.
A few presets can be used:
 - 'LOWERCASE': lower case ascii letters
 - 'UPPERCASE': uppercase ascii letters
 - 'DIGITS': digit characters
 - 'SPECIAL': Special characters

Example:

```random_str(sample=['LOWERCASE', '!@#$%']) -> 'am$y%eg$ug'```

prefix: A string to be prepended to the generated string

suffix: A string to be appended to the generated string

### set_browser_capability(capability_key, capability_value)

Set a browser capability.
This must be called before the browser is started.

### set_search_timeout(timeout)

Set the search timeout value. Timeout must be either int or float.

### set_trace()

Perform a pdb.set_trace().
The test should be run with the '-i' flag, otherwise this action will be ignored. 
Read more about the Python debugger [here](https://docs.python.org/3/library/pdb.html).

### step(message)

Add a step to the report

### store(key, value)

Store a value in data object.

### store_secret(key, value)

Store a value in the secrets object.

### take_screenshot(message='')

Take a screenshot. *message* will be used for the filename.

### timer_start(timer_name='')

Start a timer. By default start a timer with empty name. Use actions.timer_stop() to stop the timer.
Returns: the current time.

### timer_stop(timer_name='')

Stop a timer by its name. By default stops a timer with empty name. Returns: the elapsed time.

### wait(seconds)

Pause execution for the given amount of seconds.
Seconds can be an int or float.
