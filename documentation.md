Golem - Test Automation Framework
==================================================


Actions
--------------------------------------


- **add_step(message='')**

Log a new step to be displayed in the report later

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


Configuration Options
--------------------------------------

- **implicit_wait**

Default time to wait looking for an element until it is found.

- **screenshot_on_error**

Take a screenshot on error by default

- **default_driver**

Define the driver to use unless overriden by the -d/--driver flag

- **chrome_driver_path**

Full path to the chrome driver executable

- **wait_hook**

Custom wait method to use, specific to each application, must be defined inside extend.py


Command Line
--------------------------------------

- **run project test_case|test_suite [-t|--threads -d|--driver]**

Run a test case or test suite from a project. Threads indicates the amount of test cases to execute in parallel, default is 1. Driver indicates wich driver to use to run the tests, options are: firefox, chrome, default is firefox. Chrome driver requires chrome_driver_path setting to be defined in settings file.

- **gui [-p|--port]**

Start Golem GUI. Port indicates which port number to use, default is 5000.

- **startproject project**

Starts a new project with the given name. Creates the base files and folders.