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

DEPRECATED, use take screenshot instead.
Take a screenshot of the browser, the message is optional


##### clear(element)

DEPRECATED, use clear_element insteand


##### clear_element(element)

Clear element



##### click(element)

Perform a mouse click


##### close()

DEPRECATED, use close_browser instead.


##### close_browser()

Closes the webdriver browser and all it's windows/tabs


##### delete_cookie(name)
Delete a cookie from the current session.


##### delete_cookies()
Delete all cookies from the current session.

Note: this only deletes cookies from the current domain.


##### dismiss_alert()

Dismiss an alert, confirm or prompt box. Use ignore_not_present to ignore error when alert is not present.


##### double_click(element)

Double click an element


##### execute_javascript(script, *args)

Execute javascript code


##### focus_element(element)

Give focus to element


##### get(url)

Navigate to a URL, same as *navigate(url)*

##### get_alert_text()

Get text of alert, confirm or prompt box


##### get_browser()

Returns the active browser driver object


##### get_cookie(name)
Get a cookie by its name. Returns the cookie if found, None if not.


##### get_cookies()
Returns a list of dictionaries, corresponding to cookies visible in the current session.


##### get_current_url()

Returns the current browser URL


##### go_back()

Goes one step backward in the browser history


##### javascript_click(element)

Click an element using Javascript


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


##### submit_prompt_alert(text)

Send text to a prompt alert and accept it


##### set_browser_capability(capability_key, capability_value)

Set a browser capability. This must be called before the browser is started.


##### take_screenshot(message='')

Take a screenshot of entire page, the message is optional


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


##### verify_cookie_value(name, value)
Verify the value of a cookie.


##### verify_cookie_exists(name)

DEPRECATED, use verify_cookie_present instead.


##### verify_cookie_present(name)

Verify a cookie exists in the current session by the cookie name


##### verify_element_checked(element)

Verify element is checked. This applies to checkboxes and radio buttons.


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

Verify an element exists in the page


##### verify_element_not_checked(element)

Verify element is not checked. This applies to checkboxes and radio buttons.


##### verify_element_not_enabled(element)

Verify that element is not enabled


##### verify_is_enabled(element)

DEPRECATED, use verify_element_enabled


##### verify_is_not_enabled(element)

DEPRECATED, use verify_element_not_enabled


##### verify_is_not_selected(element)

DEPRECATED, use verify_element_not_checked


##### verify_is_not_visible(element)

Verify that an element is not visible


##### verify_is_selected(element)

DEPRECATED, use verify_element_checked


##### verify_is_visible(element)

Verify that an element is visible


##### verify_not_exists(element)

Verify that an element does not exist in the page


##### verify_selected_option(element, text)

DEPRECATED, use verify_selected_option_by_text or verify_selected_option_by_value


##### verify_selected_option_by_text(element, text)

Verify the option selected in a \<select\> by the option text


##### verify_selected_option(element, text)

Verify the option selected in a \<select\> by the option value


##### verify_text(text)

Verify that the given text is present anywhere on the page (in the entire DOM)


##### verify_text_in_element(element, text)

Verify that an element contains the given text.


##### wait_for_alert_present(timeout=30)

Wait for an alert to be present


##### wait_for_element_not_exist(element, timeout=20)

Wait until the element does not exists in the DOM anymore


##### wait_for_element_not_visible(element, timeout=20)

Wait until the element is not visible anymore


##### wait_for_element_enabled(element, timeout=20)

Wait until the element is enabled


##### wait_for_element_visible(element, timeout=20)

Wait until the element is visible


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

Starts an interactive console at this point of the test. The test should be run with the '-i' flag, otherwise this action will be ignored. See [Interactive Mode](Interactive-mode.html) for more details.


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


##### refresh_page()

Refreshes the page


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

##### http_get(url, headers, params)

Perform an HTTP GET request to the URL, with the given headers and params. Headers and params must be Python dicts and are optional. The response is stored in 'data.last_response'

Example:
```
http_get('http://google.com/')
assert_equals(data.last_response.status_code, 200)
```


##### http_post(url, headers, data)

Perform an HTTP POST request to the URL, with the given headers and data. Headers and params must be Python dicts and are optional. The response is stored in 'data.last_response'




Next, go to [Custom Actions](custom-actions.html)
