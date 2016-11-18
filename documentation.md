Golem - Test Automation Framework
==================================================


Actions
--------------------------------------


- **capture(message='')**

Take a screenshot of the browser, the message is optional

 - **click(element)**

Perform a click

- **close()**

Closes the webdriver browser

 - **go_to(url)**

Navigate to a URL

- **select_by_index(element, text)**

Select an option from a <select> by the index of the option

- **select_by_text(element, text)**

Select an option from a <select> by the option text

- **select_by_value(element, value)**

Select an option from a <select> by the option value. For example:
```
<select>
    <option value="AR">Argentina</option>
    <option value="BR">Brazil</option>
</select>
```

- **send_keys(element, text)**

Perform a click

- **store(key, value)**

Store a value in the given key for later use

- **verify_exists(element)**

Verify an element exists in the page

- **verify_is_enabled(element)**

Verify an element is enabled

- **verify_is_not_enabled(element)**

Verify an element is not enabled

- **verify_not_exists(element)**

Verify an element does not exist in the page

- **verify_selected_option(element, text)**

Verify that the option selected in a <select> is the one given (by the option text)

- **verify_text(text)**

Verify the given text is present anywhere on the page (entire DOM)

- **verify_text_in_element(element, text)**

Verify that an element contains the given text.

- **wait(seconds)**

Pause execution for the given amount of seconds