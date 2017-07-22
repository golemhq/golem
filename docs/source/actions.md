Golem Actions
==================================================

Golem comes with predefined actions that cover almost all the needs to write tests. They are self-documenting. The entire list of available actions is the following:


- **add_step(message)**

Logs a new step to be displayed in the report later

- **capture(message='')**

Take a screenshot of the browser, the message is optional

- **click(element)**

Perform a mouse click

- **close()**

Closes the webdriver browser

- **go_to(url)**

Navigate to a URL

- **random(args)**

Generate a random string

- **select_by_index(element, text)**

Select an option from a \<select\> element by the index of the option

- **select_by_text(element, text)**

Select an option from a \<select\> element by the option text

- **select_by_value(element, value)**

Select an option from a \<select\> element by the option value. 

For example, given:

```
<select>
    <option value="CA">Canada</option>
    <option value="US">United States</option>
    <option value="MX">Mexico</option>
</select>
```

To select the first option You could use:

```
select_by_index(elem, 0)
select_by_text(elem, 'Canada')
select_by_value(elem, 'CA')
```


- **send_keys(element, text)**

Send key strokes to the element

- **store(key, value)**

Store a value in the given key for later use. The value is going to be available through the data dictionary.

- **verify_exists(element)**

Verify an element exists in the page

- **verify_is_enabled(element)**

Verify an element is enabled

- **verify_is_not_enabled(element)**

Verify an element is not enabled

- **verify_not_exists(element)**

Verify an element does not exist in the page

- **verify_selected_option(element, text)**

Verify that the option selected in a \<select\> is the one given (by the option text)

- **verify_text(text)**

Verify the given text is present anywhere on the page (in the entire DOM)

- **verify_text_in_element(element, text)**

Verify that an element contains the given text.

- **wait(seconds)**

Pause execution for the given amount of seconds

- **wait_for_element_not_visible(element, timeout=20)**

Pause execution for the given amount of seconds until the element is no longer visible (default is 20 seconds)

- **wait_for_element_visible(element, timeout=20)**

Pause execution for the given amount of seconds until the element is visible (default is 20 seconds)

- **wait_for_element_enabled(element, timeout=20)**

Pause execution for the given amount of seconds until the element is enabled (default is 20 seconds)

Next, go to [Custom Actions](custom-actions.html)