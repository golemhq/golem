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