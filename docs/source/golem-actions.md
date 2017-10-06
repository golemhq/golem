Golem Actions
==================================================

Golem comes with predefined actions that cover almost all the needs to write tests. They are self-documenting. The entire list of available actions is the following:


### Browser Actions


##### capture(message='')

Take a screenshot of the browser, the message is optional


##### clear(element)

Clear element


##### click(element)

Perform a mouse click


##### close()

Closes the webdriver browser


##### mouse_hover(element)

Perform a mouse hover on the element


##### navigate(url)

Navigate to a URL


#####press_key(element, key)

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


##### step(message)

Logs a new step to be displayed in the report later


##### store(key, value)

Store a value in the given key for later use. Th_e value is going to be available through the data dictionary.


##### wait(seconds)

Pause execution for the given amount of seconds


### API Actions

##### get(url, headers, data)

Perform a get HTTP request to the URL, with the given headers and data. The response is stored in 'data.last_response'


##### post(url, headers, data)

Perform a post HTTP request to the URL, with the given headers and data. The response is stored in 'data.last_response'




Next, go to [Custom Actions](custom-actions.html)
