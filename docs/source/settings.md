Settings
==================================================

Use the settings.json file to configure Golem behavior. There is a global settings.json file and a settings.json file inside each project folder.

<div class="admonition note">
    <p class="first admonition-title">Remember</p>
    <p>The settings defined inside a project will override the global settings for that project</p>
</div>

#### Settings


- *implicit_wait*

Default time to wait looking for an element until it is found. Default is 20 seconds.

- *screenshot_on_error*

Take a screenshot on error by default. Default is True.

- *screenshot_on_step*

Take a screenshot on every step. Default is False.

- *screenshot_on_end*

Take a screenshot after 'test' function ends. Default is False.

- *test_data*

The location to store test data. Options are: 'infile' and 'csv'. Default is 'csv.'. 

With 'test_data' = 'infile'  data is stored inside the test file as a list of dictionaries. 

With 'test_data' = 'csv' data is stored in a csv file in the same folder of the test and with the same name, e.g.: /tests/some_test.py -> /tests/some_test.csv

- *wait_hook*

Custom wait method to use for every action, that can be specific to each application. It must be defined inside extend.py

- *default_browser*

Define the driver to use unless overriden by the -d/--driver flag. Default is 'chrome'. Valid options are: firefox, chrome, chrome-remote, firefox-remote, chrome-headless, chrome-remote-headless.

- *chromedriver_path*

Path to the chrome driver executable. By default it points to the *drivers* folder inside the test directory.

- *geckodriver_path*

Path to the gecko driver executable. By default it points to the *drivers* folder inside the test directory.

- *remote_url*

the URL to use when connecting to a remote webdriver, for example, when using selenium grid. Default is 'http://localhost:4444/wd/hub'

- *remote_browsers*

Define a list of remote browsers with it's capabilities, required to run tests with Selenium Grid or another remote device provider such as SauceLabs.
The minimum capabilities required are 'browserName', 'version' and 'platform', read [this](https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities) for more info.

Example: settings.json
```
{

"remote_browsers": {
        "chrome_60_mac": {
            "browserName": "chrome",
            "version": "60.0",
            "platform": "macOS 10.12"
        },
        "firefox_56_windows": {
            "browserName": "firefox",
            "version": "56.0",
            "platform": "Windows 10"
        }
    }

}
```

- *console_log_level*

Default is 'INFO'

- *log_all_events*

Default is false

<br>

Next, go to [Browser Web Drivers](browser-web-drivers.html)