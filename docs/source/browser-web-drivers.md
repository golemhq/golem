Browser Web Drivers
==================================================

The supported browsers are:
- Chrome
- Edge
- Firefox
- Internet Explorer
- Opera
- Remote (Selenium Grid)

To download the webdriver executables run the following command (currently only Chrome and Firefox):

```
webdriver-manager update
```

**A note on driver versions**

When using a search pattern like: ```"chromedriver_path": "./drivers/chromedriver*"``` Golem will automatically choose the highest version available.

Example, consider the following files:
```
/drivers
    chromedriver_2.36
    chromedriver_2.37
    chromedriver_2.38
```

When using ```"chromedriver_path": "./drivers/chromedriver*"``` the chromedriver_2.38 will be selected.

<br>

To download the executables manually, follow instructions below.


#### Chrome  

Download the Chromedriver from [http://chromedriver.chromium.org/downloads](http://chromedriver.chromium.org/downloads)

Set the *chromedriver_path* setting to point to the location of the chromedriver, e.g. ```"chromedriver_path": "./drivers/chromedriver*"```

##### Chrome headless

Chrome can run in headless mode, without a GUI. Set the browser of a test or suite to 'chrome-headless' or 'chrome-remote-headless.

Requirements: chrome 58+, chromedriver 2.32+

```
golem run <project> <test> -b chrome-headless
```


#### Firefox

Download the Geckodriver from [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)

Set the *geckodriver_path* setting to point to the location of the geckodriver, e.g. ```"geckodriver_path": "./drivers/geckodriver*"```


#### Internet Explorer

Download the IEDriverServer from [http://selenium-release.storage.googleapis.com/index.html](http://selenium-release.storage.googleapis.com/index.html).

Set the *iedriver_path* setting to point to the location of the iedriver, e.g. ```"iedriver_path": "./drivers/iedriver*"```


#### Edge

Download the Edge driver from [https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).

Set the *edgedriver_path* setting to point to the location of the edgedriver, e.g. ```"edgedriver_path": "./drivers/edgedriver*"```


#### Opera

Download the Opera driver from [https://github.com/operasoftware/operachromiumdriver/releases](https://github.com/operasoftware/operachromiumdriver/releases).

Set the *operadriver_path* setting to point to the location of the Opera driver, e.g. ```"operadriver_path": "./drivers/operadriver*"```

##### Error: cannot find Opera binary

The Opera driver fails to find the Opera binary installed in the machine. To fix this set the *opera_binary_path* setting to point to the Opera binary. Example:

```
"opera_binary_path": "C:\\Program Files\\Opera\\launcher.exe", 
```

<br>

Next, go to [Interactive Mode](Interactive-mode.html)
