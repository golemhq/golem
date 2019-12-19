Settings
==================================================

Settings are defined in the settings.json file. They modify certain Golem behaviors.
There is a global settings.json file and a project settings.json file.
Note: project settings override global settings.


## Setting List


### search_timeout

Default time to wait looking for an element until it is present. Default is 20 seconds.

### wait_displayed

Wait for elements to be present and displayed. Default is False

### screenshot_on_error

Take a screenshot on error by default. Default is True.

### screenshot_on_step

Take a screenshot on every step. Default is False.

### screenshot_on_end

Take a screenshot after 'test' function ends. Default is False.

### test_data

The location to store test data. Options are: 'infile' and 'csv'. Default is 'csv.'. 

With 'test_data' = 'infile'  data is stored inside the test file as a list of dictionaries. 

With 'test_data' = 'csv' data is stored in a csv file in the same folder of the test and with the same name, e.g.: /tests/test1.py -> /tests/test1.csv

### wait_hook

Custom wait method to use for every action, that can be specific to each application. It must be defined inside extend.py

### default_browser

Define the driver to use unless overriden by the -b/--browsers flag. Default is 'chrome'. The valid options are listed [here](browsers.html#valid-options).

### chromedriver_path

Path to the Chrome driver executable.

### edgedriver_path

Path to the Edge driver executable.

### geckodriver_path

Path to the Gecko driver executable.

### iedriver_path

Path to the Internet Explorer driver driver executable.

### operadriver_path

Path to the Opera driver executable.

### opera_binary_path

The path to the Opera binary file. Used to fix "Error: cannot find Opera binary" error.

### remote_url

The URL to use when connecting to a remote webdriver, for example, when using selenium grid. Default is 'http://localhost:4444/wd/hub'

### remote_browsers

Defines a list of remote browsers with its capabilities, required to run tests with Selenium Grid or another remote device provider.
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


### implicit_actions_import
Import golem.actions module implicitly to the tests.
Modifies test saving behavior when using the GUI test builder.
Default is true.

### implicit_page_import
Import pages implicitly to the test from a list of strings.
When true, imported pages are saved as a list of strings. When false, import statements are used instead.
Default is true.

### screenshots

Modify screenshot format, size, and quality before saving to disk.

Requires Pillow to be installed. It must be installed separately: ```pip install pillow```

It should be an object with the following attributes: format, quality, width, height, and resize

* **format**: "jpg" or "png". The default is "png".
* **quality**: an int in 1..95 range. The default is 75. This only applies to "jpg" files.
* **width**: defines the width of screenshots. If "height" is not set, this will maintain the aspect ratio.
* **height**: defines the height of screenshots. If "width" is not set, this will maintain the aspect ratio.
* **resize**: the percentage to resize screenshots. Must be int or string in the format "55" or "55%". To resize by percentage do not set width or height.

Example:
```JSON
{
    "screenshots": {
        "format": "jpg",
        "quality": 50,
        "resize": 70
    }
}
```

### console_log_level

Deprecated, use *cli_log_level*.

### cli_log_level

command line log level.
Options are: DEBUG, INFO, WARNING, ERROR, CRITICAL. Default is INFO.

### log_all_events

Log all events or just Golem events. Default is true.

### start_maximized

Start the browser maximized. Default is true.