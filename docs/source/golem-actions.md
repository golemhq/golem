Golem Actions
==================================================

Golem comes with predefined actions that cover almost all the needs to write tests. They are self-documenting. The entire list of available actions is the following:


### Browser Actions


##### accept_alert()

Accepts an alert present


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

Take a screenshot of the browser, the message is optional


##### clear(element)

Clear element


##### click(element)

Perform a mouse click


##### close()

Closes the webdriver browser


##### delete_cookie(name)
Delete a cookie from the current session.


##### delete_cookies()
Delete all cookies from the current session.

Note: this only deletes cookies from the current domain.


##### dismiss_alert()
Dismiss an alert


##### get(url)

Navigate to a URL, same as *navigate(url)*


##### get_browser()

Returns the active browser driver object


##### get_cookie(name)
Get a cookie by its name. Returns the cookie if found, None if not.


##### get_cookies()
Returns a list of dictionaries, corresponding to cookies visible in the current session.


##### get_current_url()

Returns the current browser URL


##### mouse_hover(element)

Perform a mouse hover on the element


##### navigate(url)

Navigate to a URL


##### open_browser(browser_id=None)

Open a new browser. Browser Id is optional, useful when having multiple open browsers.


##### press_key(element, key)

Press the given keyboard key on the element. Options are:

* ENTER/RETURN
* UP
* DOWN
* LEFT
* RIGHT


##### select_by_index(element, text)

Select an option from a \<select\> element by the index of the option


##### select_by_text(element, text)

Select an option from a \<select\> element by the option text


##### select_by_value(element, value)

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
select_by_index('#countrySelect', 0)
select_by_text('#countrySelect', 'Canada')
select_by_value('#countrySelect', 'CA')
```


##### send_keys(element, text)

Send key strokes to the element

##### set_browser_capability(capability_key, capability_value)
Set a browser capability. Must be called before the browser is started.


##### verify_alert_is_present()

Verify an alert is present


##### verify_alert_is_not_present()

Verify an alert is not present


##### verify_cookie_value(name, value)
Verify the value of a cookie.


##### verify_cookie_exists(name)
Verify a cookie exists in the current session. The cookie is found by its name.

##### verify_exists(element)

Verify an element exists in the page


##### verify_is_enabled(element)

Verify that an element is enabled


##### verify_is_not_enabled(element)

Verify that an element is not enabled


##### verify_is_not_selected(element)

Verify that an element is not selected, i.e: a checkbox


##### verify_is_not_visible(element)

Verify that an element is not visible


##### verify_is_selected(element)

Verify that an element is selected, i.e.: a checkbox


##### verify_is_visible(element)

Verify that an element is visible


##### verify_not_exists(element)

Verify that an element does not exist in the page


##### verify_selected_option(element, text)

Verify that the option selected in a \<select\> is the one given (by the option text)


##### verify_text(text)

Verify that the given text is present anywhere on the page (in the entire DOM)


##### verify_text_in_element(element, text)

Verify that an element contains the given text.


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

Assert that the element contains the value


##### assert_equals(actual, expected)

Assert that the actual value equals the expected value


##### assert_false(condition)

Assert that the condition is false


##### assert_true(condition)

Assert that the condition is true


##### debug()

Starts an interactive console at this point of the test. The test should be run with the '-i' flag, otherwise it will be ignored. See [Interactive Mode](Interactive-mode.html) for more details.


##### random(args)

Generate a random string. Options:

* 'c' generate a random lowercase letter
* 'd' generate a random digit

For example: random('cccddd') => 'aeg147'


##### refresh_page()

Refreshes the page


##### step(message)

Logs a new step to be displayed in the report later


##### store(key, value)

Store a value in the given key for later use. Th_e value is going to be available through the data dictionary.


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
