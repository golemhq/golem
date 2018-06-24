Golem Actions
==================================================

Golem comes with predefined actions that cover almost all the needs to write tests. They are self-documenting. The entire list of available actions is the following:


### Browser Actions


##### accept_alert(ignore_not_present=False)

Accepts an alert, confirm or prompt box. Use ignore_not_present to ignore error when alert is not present.


##### activate_browser(browser_id)

Activates a browser to use in subsequent actions. Only needed when having more than one browser open.


##### add_cookie(cookie_dict)

Add a cookie to the current session.
    
Required keys are: "name" and "value". Optional keys are: "path", "domain", "secure", "expiry"

Note:
* If a cookie with the same name exists, it will be overriden.
* This function cannot set the domain of a cookie, the domain URL
must be visited by the browser first.
* The domain is set automatically to the current domain the browser is in.
* If the browser did not visit any url (initial blank page) this
function will fail with "Message: unable to set cookie"

**Example usage:**

add_cookie({'name': 'foo', 'value': 'bar'})


##### capture(message='')

DEPRECATED, use take_screenshot instead.
Take a screenshot of the browser, the message is optional


##### check_element(element)

Check an element (checkbox or radiobutton). If element is already checked this is is ignored.


##### clear(element)

DEPRECATED, use clear_element instead


##### clear_element(element)

Clear element


##### click(element)

Perform a mouse click


##### close()

DEPRECATED, use close_browser or close_window instead.


##### close_browser()

Closes the webdriver browser and all it's windows/tabs


##### close_window()

Close current window/tab.
If there is only one window, this will close the browser, use close_browser instead.
If there are other windows open, this will switch to the first window afterwards.


##### close_window_by_index()

Close window/tab by index. Note: "The order in which the window handles are returned is arbitrary."


##### close_window_by_partial_title(partial_title)

Close window/tab by partial title


##### close_window_by_partial_url(partial_url)

Close window/tab by partial URL


##### close_window_by_title(title)

Close window/tab by title


##### close_window_by_url(url)

Close window/tab by URL


##### delete_cookies()

Delete all cookies from the current session. Note: this only deletes cookies from the current domain.


##### delete_cookie(name)

Delete a cookie from the current session.


##### dismiss_alert()

Dismiss an alert, confirm or prompt box. When ignore_not_present is True the error when alert is not present is ignored.


##### double_click(element)

Double click an element


##### execute_javascript(script, *args)

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


##### focus_element(element)

Give focus to element


##### get(url)

Navigate to a URL, same as *navigate(url)*


##### get_active_element()

Returns the element with focus, or BODY if nothing has focus


##### get_alert_text()

Get text of alert, confirm or prompt box


##### get_browser()

Returns the active browser driver object


##### get_cookie(name)

Get a cookie by its name. Returns the cookie if found, None if not


##### get_cookies()

Returns a list of dictionaries, corresponding to cookies present in the current session.


##### get_current_url()

Returns the current browser URL


##### get_element_attribute(element, attribute)

Get the attribute value of element. If the attribute is not present in element, None is returned.
   

##### get_element_text(element)

Get the element text


##### get_element_value(element)

Get the element value attribute


##### get_page_source()

Get the entire source code of the page


##### get_window_handle()


##### get_window_handles()

Return a list with the handles of all the open windows/tabs


##### get_window_index()

Get the index of the current window/tab


##### get_window_title()


##### get_window_titles()

Return a list with the titles of all the open windows/tabs


##### go_back()

Goes one step backward in the browser history


##### go_forward()

Goes one step forward in the browser history


##### javascript_click(element)

Click an element using Javascript


##### maximize_window()


##### mouse_hover(element)

DEPRECATED, use mouse_over instead


##### mouse_over(element)

Perform a mouse over on the element


##### navigate(url)

Navigate to a URL


##### open_browser(browser_id=None)

Open a new browser. Browser Id is optional, useful when having multiple open browsers.


##### press_key(element, key)

Press a given key in the element.
Key must be a string with a value defined in selenium.webdriver.common.keys.Keys

Examples:
```
press_key('ENTER')
press_key('TAB')
press_key('LEFT')
```


##### refresh_page()

Refreshes the page


##### select_by_index(element, text)

DEPRECATED, use select_option_by_index instead


##### select_by_text(element, text)

DEPRECATED, use select_option_by_text instead


##### select_by_value(element, value)

DEPRECATED, use select_option_by_value instead


##### select_option_by_index(element, text)

Select an option from a \<select\> element by index (starts from 0)


##### select_option_by_text(element, text)

Select an option from a \<select\> element by the option text


##### select_option_by_value(element, value)

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


##### send_keys(element, text)

Send text to element


##### send_text_to_alert(text)

Send text to an alert


##### set_browser_capability(capability_key, capability_value)

Set a browser capability. This must be called before the browser is started.


##### submit_prompt_alert(text)

Send text to a prompt alert and accept it


##### submit_form(element)

Submit form. Element can be the form itself or any child element.


##### switch_to_default_content()

Switch to default content (default frame)


##### switch_to_first_window()

Switch to first window/tab (in the list of window handles)


##### switch_to_frame(frame)

Switch to frame. frame must be the index, name, or the frame webelement itself.


##### switch_to_last_window()

Switch to last window/tab (in the list of window handles)


##### switch_to_next_window()

Switch to next window/tab in the list of window handles. If current window is the last in the list this will circle back from the start.


##### switch_to_parent_frame()

Switch to the parent of the current frame


##### switch_to_next_window()

Switch to previous window/tab in the list of window handles. If current window is the first in the list this will circle back from the top.


##### switch_to_window_by_index(index)

Switch to window/tab by index. Note: "The order in which the window handles are returned is arbitrary."


##### switch_to_window_by_partial_title(partial_title)

Switch to window/tab by partial Title


##### switch_to_window_by_title(title)

Switch to window/tab by title


##### switch_to_window_by_url(url)

Switch to window/tab by title


##### switch_to_window_by_partial_url(partial_url)

Switch to window/tab by partial URL


##### take_screenshot(message='')

Take a screenshot of the entire page, the message is optional


##### uncheck_element(checkbox)

Uncheck a checkbox. If element is already checked this is is ignored.


##### verify_alert_is_present()

DEPRECATED, use verify_alert_present


##### verify_alert_is_not_present()

DEPRECATED, use verify_alert_not_present


##### verify_alert_present()

Verify an alert is present. This applies to alerts, confirms and prompts.


##### verify_alert_not_present()

Verify an alert is not present. This applies to alerts, confirms and prompts.


##### verify_alert_text(text)

Verify alert text


##### verify_alert_text_is_not(text)

Verify alert text is not text


##### verify_amount_of_windows(amount)

Verify the amount of open windows/tabs


##### verify_cookie_value(name, value)
Verify the value of a cookie.


##### verify_cookie_exists(name)

DEPRECATED, use verify_cookie_present instead.


##### verify_cookie_present(name)

Verify a cookie exists in the current session by the cookie name


##### verify_element_attribute(element, attribute, value)

Verify the value of attribute of element


##### verify_element_attribute_is_not(element, attribute, value)

Verify the value of attribute of element is not 'value'


##### verify_element_checked(element)

Verify element is checked. This applies to checkboxes and radio buttons.


##### verify_element_displayed(element)

Verify element is displayed


##### verify_element_enabled(element)

Verify that element is enabled


##### verify_element_has_attribute(element, attribute)

Verify element has attribute


##### verify_element_has_focus(element)

Verify element has focus


##### verify_element_has_not_attribute(element, attribute)

Verify element does not have attribute


##### verify_element_has_not_focus(element)

Verify element does not have focus


##### verify_exists(element)

DEPRECATED, use verify_element_present


##### verify_element_not_checked(element)

Verify element is not checked. This applies to checkboxes and radio buttons.


##### verify_element_not_enabled(element)

Verify that element is not enabled


##### verify_element_not_displayed(element)

Verify element is not displayed


##### verify_element_not_present(element)

Verify element is not present in the DOM


##### verify_element_present(element)

Verify element is present in the DOM


##### verify_element_text(element, text)

Verify the text of the element


##### verify_element_text_contains(element, text)

Verify element contains text


##### verify_element_text_is_not(element, text)

Verify the text of the element is not text


##### verify_element_text_not_contains(element, text)

Verify element does not contain text


##### verify_is_enabled(element)

DEPRECATED, use verify_element_enabled


##### verify_is_not_enabled(element)

DEPRECATED, use verify_element_not_enabled


##### verify_is_not_selected(element)

DEPRECATED, use verify_element_not_checked


##### verify_is_not_visible(element)

DEPRECATED, use verify_element_not_displayed


##### verify_is_selected(element)

DEPRECATED, use verify_element_checked


##### verify_is_visible(element)

DEPRECATED, use verify_element_displayed


##### verify_not_exists(element)

DEPRECATED, use verify_element_not_present


##### verify_page_contains_text(text)

Verify the given text is present anywhere in the page (in the entire DOM)


##### verify_page_not_contains_text(text)

Verify the given text is present anywhere in the page (in the entire DOM)


##### verify_selected_option(element, text)

DEPRECATED, use verify_selected_option_by_text or verify_selected_option_by_value


##### verify_selected_option_by_text(element, text)

Verify the option selected in a \<select\> by the option text


##### verify_selected_option_by_value(element, text)

Verify the option selected in a \<select\> by the option value


##### verify_text(text)

DEPRECATED, use verify_page_contains_text


##### verify_text_in_element(element, text)

DEPRECATED, use verify_element_text or verify_element_text_contains


##### verify_title(title)

Verify the page title


##### verify_title_contains(partial_title)

Verify the page title contains partial_title


##### verify_title_is_not(title)

Verify the page title is not title


##### verify_title_not_contains(text)

Verify the page title does not contain text


##### verify_url(url)

Verify the current URL


##### verify_url_contains(partial_url)

Verify the current URL contains partial_url


##### verify_url_is_not(url)

Verify the current URL is not url


##### verify_url_not_contains(partial_url)

Verify the current URL does not contain partial_url


##### verify_window_present_by_partial_title(title)

Verify there is a window/tab present by partial title


##### verify_window_present_by_partial_url(partial_url)

Verify there is a window/tab present by partial URL


##### verify_window_present_by_title(title)

Verify there is a window/tab present by title


##### verify_window_present_by_url(url)

Verify there is a window/tab present by URL


##### wait_for_alert_present(timeout=30)

Wait for an alert to be present


##### wait_for_element_displayed(element, timeout=30)

Wait for element to be present and displayed


##### wait_for_element_enabled(element, timeout=30)

Wait for element to be enabled


##### wait_for_element_has_attribute(element, attribute timeout=30)

Wait for element to have attribute


##### wait_for_element_has_not_attribute(element, attribute timeout=30)

Wait for element to not have attribute


##### wait_for_element_not_displayed(element, timeout=30)

Wait for element to be not displayed


##### wait_for_element_not_enabled(element, timeout=30)

Wait for element to be not enabled


##### wait_for_element_not_exist(element, timeout=20)

DEPRECATED, use wait_for_element_not_present


##### wait_for_element_not_present(element, timeout=30)

Wait for element to stop being present in the DOM. If element is already not present, this will be ignored.


##### wait_for_element_not_visible(element, timeout=20)

DEPRECATED, use wait_for_element_not_displayed


##### wait_for_element_present(element, timeout=30)

Wait for element to be present in the DOM


##### wait_for_element_text(element, text, timeout=30)

Wait for element text to match given text


##### wait_for_element_text_contains(element, text, timeout=30)

Wait for element text to contain given text


##### wait_for_element_text_is_not(element, text, timeout=30)

Wait for element text to not match given text


##### wait_for_element_text_not_contains(element, text, timeout=30)

Wait for element text to not contain given text


##### wait_for_element_visible(element, timeout=20)

DEPRECATED, use wait_for_element_displayed


##### wait_for_page_contains_text(text, timeout=30)

Wait for page to contain text in the DOM


##### wait_for_page_not_contains_text(text, timeout=30)

Wait for page to not contain text in the DOM


##### wait_for_title(title, timeout=30)

Wait for page title to be the given value


##### wait_for_title_contains(partial_title, timeout=30)

Wait for page title to contain partial_title


##### wait_for_title_is_not(title, timeout=30)

Wait for page title to not be the given value


##### wait_for_title_not_contains(partial_title, timeout=30)

Wait for page title to not contain partial_title


##### wait_for_window_present_by_partial_title(partial_title, timeout=30)

Wait for window/tab present by partial title


##### wait_for_window_present_by_partial_url(partial_url, timeout=30)

Wait for window/tab present by partial url


##### wait_for_window_present_by_title(title, timeout=30)

Wait for window/tab present by title


##### wait_for_window_present_by_url(url, timeout=30)

Wait for window/tab present by url


### General Actions


##### assert_contains(element, value)

DEPRECATED. Assert that the element contains the value


##### assert_equals(actual, expected)

DEPRECATED. Assert that the actual value equals the expected value


##### assert_false(condition)

DEPRECATED. Assert that the condition is false


##### assert_true(condition)

DEPRECATED. Assert that the condition is true


##### debug()

DEPRECATED, use interactive_mode instead.


##### error(message='')

Mark the test as error and stop


#### fail(message='')

Mark the test as failure and stop


##### get_search_timeout()

Get search timeout.


##### interactive_mode()

Starts an interactive console at this point of the test. The test should be run with the '-i' flag, otherwise this action will be ignored. See [Interactive Mode](Interactive-mode.html) for more details.


##### random(args)

Generate a random string. Options:

* 'c' generate a random lowercase letter
* 'd' generate a random digit

For example: random('cccddd') => 'aeg147'



##### set_search_timeout(timeout)

Set the search timeout value. Timeout must be either int or float.


##### set_trace()

Perform a pdb.set_trace().
Read more about the Python debugger [here](https://docs.python.org/3/library/pdb.html).
The test should be run with the '-i' flag, otherwise this action will be ignored 


##### set_window_size(width, height)

Set the width and height of the window (in pixels)


##### step(message)

Logs a new step to be displayed in the report


##### store(key, value)

Store a value in the given key for later use. The value is going to be available through the data dictionary.


##### wait(seconds)

Pause execution for the given amount of seconds


### API Actions (Alpha)


##### http_get(url, headers={}, params={})

Perform an HTTP GET request to the URL, with the given headers and params.
Headers and params must be Python dictionaries and are optional. The response is stored in 'data.last_response'

Example:
```
http_get('http://google.com/')
assert_equals(data.last_response.status_code, 200)
```


##### http_post(url, headers={}, data={}, verify_ssl_cert=True)

Perform an HTTP POST request to the URL, with the given headers and data.
Headers and params must be Python dictionaries and are optional. The response is stored in 'data.last_response'


##### verify_response_status_code(response, status_code)

Verify response status code



Next, go to [Custom Actions](custom-actions.html)
