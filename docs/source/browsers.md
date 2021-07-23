Browsers
==================================================

## Supported Browsers

The supported browsers are:
- Chrome
- Edge
- Firefox
- Internet Explorer
- Opera
- Remote (Selenium Grid)

## Webdriver Manager

To download the Webdriver executables run the following command (currently only Chrome and Firefox):

```
webdriver-manager update
```

List the current downloaded versions:

```
webdriver-manager versions
```

Download a specific Webdriver:

```
webdriver-manager update -d chrome
```


To learn more about the Webdriver Manager see: <https://github.com/golemhq/webdriver-manager>


### Webdriver Executables

Each browser requires its own Webdriver executable. These can be downloaded manually from these locations:

* Chrome: <https://sites.google.com/a/chromium.org/chromedriver/downloads>
* Firefox: <https://github.com/mozilla/geckodriver/releases>
* IE: <http://selenium-release.storage.googleapis.com/index.html>
* Edge: <https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/>
* Opera: <https://github.com/operasoftware/operachromiumdriver/releases>

## Path to the Webdriver Executables

Golem needs to know where to find the executables for each of the required browsers.
This is accomplished by the *settings.json* file.
By default it points to the *drivers* folder inside the Test Directory:

```json
{
  "chromedriver_path": "./drivers/chromedriver*",
  "edgedriver_path": "./drivers/edgedriver*",
  "geckodriver_path": "./drivers/geckodriver*",
  "iedriver_path": "./drivers/iedriver*",
  "operadriver_path": "./drivers/operadriver*"
}
```

When using a search pattern like: ```"chromedriver_path": "./drivers/chromedriver*"``` Golem will automatically choose the highest version available.
In the next case, *chromedriver_2.38* will be selected:
```text
/drivers
    chromedriver_2.36
    chromedriver_2.37
    chromedriver_2.38
```


### Error: cannot find Opera binary

The Opera driver fails to find the Opera binary installed in the machine. To fix this set the *opera_binary_path* setting to point to the Opera binary. Example:

```
"opera_binary_path": "C:\\Program Files\\Opera\\launcher.exe", 
```



## Specifying the Browser For a Test

The browser (or browsers) that a test or suite will use can be specified from a few places:


1. From the run command:

    ```bash
    golem run project_name test_name -b chrome firefox
    ```

2. From a suite:

    ```python
    browsers = ['chrome', 'firefox']
    ```

3. Using the *default_browser* setting:

    ```
    "default_browser": "chrome"
    ```


### Valid options:
* chrome
* chrome-headless
* chrome-remote
* chrome-remote-headless
* edge
* edge-remote
* firefox
* firefox-headless
* firefox-remote
* firefox-remote-headless
* ie
* ie-remote
* opera
* opera-remote
* any remote browser defined in settings


### Chrome Headless

Chrome can run in headless mode (without a GUI). Set the browser of a test or suite to 'chrome-headless' or 'chrome-remote-headless'.

Requirements: chrome 58+, chromedriver 2.32+

```
golem run <project> <test> -b chrome-headless
```

### Firefox Headless

Chrome can run in headless mode (without a GUI). Set the browser of a test or suite to 'firefox-headless' or 'firefox-remote-headless'.

```
golem run <project> <test> -b firefox-headless
```

## Working with the Browser

### Opening and Closing the Browser

There is no need to open or close the browser.
The first action that requires a browser will open one.
At the end of the test, Golem will close the browser.
However, this can be done explicitly with the *open_browser* and *close_browser* actions.


### Retrieving the Open Browser

During the execution of a test the open browser is located in the execution module:

```python
from golem import execution

print(execution.browser.title)
```

A shortcut to this is using the *get_browser* action:

```python
from golem import actions

print(actions.get_browser().title)
```

## Custom Browser Boot Up

To have full control over the configuration of a WebDriver instance a custom browser boot up function can be defined.

Custom browsers are defined inside a **browsers.py** module in the folder of a project.

Custom browser functions receive the settings dictionary and must return an instance of a GolemXDriver class
(golem.webdriver.*GolemChromeDriver*, golem.webdriver.*GolemGeckoDriver*, golem.webdriver.*GolemRemoteDriver*, etc.)

projects/my_project/browsers.py
```python
from selenium import webdriver
from golem.webdriver import GolemChromeDriver

def my_custom_chrome(settings):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=800,600")
    executable_path = 'path/to/chromedriver'
    return GolemChromeDriver(executable_path=executable_path,
                             chrome_options=chrome_options)
```

Then use it:

```
golem run my_project . -b my_custom_chrome
```

The following custom browser uses the version matching mechanism to get the latest executable from the /drivers folder:

```python
from selenium import webdriver
from golem.core.utils import match_latest_executable_path
from golem import execution
from golem.webdriver import GolemChromeDriver

def my_custom_chrome(settings):
    executable_path = settings['chromedriver_path']
    matched_executable_path = match_latest_executable_path(executable_path,
                                                           execution.testdir)
    return GolemChromeDriver(executable_path=matched_executable_path,
                             chrome_options=chrome_options)
```

A custom Firefox:
```python
from selenium.webdriver.firefox.options import Options
from golem.core.utils import match_latest_executable_path
from golem import execution
from golem.webdriver import GolemGeckoDriver

def my_custom_firefox(settings):
    executable_path = settings['geckodriver_path']
    matched_executable_path = match_latest_executable_path(executable_path,
                                                           execution.testdir)
    options = Options()
    options.add_argument("--headless")
    return GolemGeckoDriver(executable_path=matched_executable_path, options=options)
```

A custom remote browser
```python
from golem.webdriver import GolemRemoteDriver

def my_custom_remote_driver(settings):
    capabilities = {
        'browserName': 'chrome',
        'platform': 'WINDOWS',
        'version': ''
    }
    grid_url = 'http://localhost:4444'
    return GolemRemoteDriver(command_executor=grid_url,
                             desired_capabilities=capabilities)
```