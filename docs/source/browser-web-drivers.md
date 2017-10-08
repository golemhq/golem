Browser Web Drivers
==================================================


### Chrome

To run tests using Chrome, the Chromedriver executable is needed.

ChromeDriver is a standalone server which implements WebDriver's wire protocol for Chromium. ChromeDriver is available for Chrome on Android and Chrome on Desktop (Mac, Linux, Windows and ChromeOS).  

Download Chromedriver from [here](https://sites.google.com/a/chromium.org/chromedriver/)

To set it up for Golem to use, place it anywhere in your machine (you can use the 'drivers' folder that is generated automatically inside the test directory) and point to it with the 'chromedriver_path' settings variable:

**settings.json**
```
"chromedriver_path": "./drivers/chromedriver",
```

#### Chrome headless

Chrome can run in headless mode, without a GUI. This is useful when running tests in servers without display.

To do this, just set the browser of a test or suite to 'chrome-headless' or 'chrome-remote-headless.

Requirements: chrome 58+, chromedriver 2.32+

```
python golem.py run project_name test_name -b chrome-headless
```


### Firefox

Firefox needs the geckodriver to work.

Download the Geckodriver from [here](https://github.com/mozilla/geckodriver/releases)

Point to the geckodriver executable using the settings 'geckodriver_path' variable:

**settings.json**
```
geckodriver_path": "./drivers/geckodriver",
```


### Internet Explorer

Internet Explorer needs the IEDriverServer executable to work.

Download the IEDriverServer from [here](http://selenium-release.storage.googleapis.com/index.html).

Point to the IEDriverServer executable using the settings 'iedriver_path' variable:

**settings.json**
```
iedriver_path": "./drivers/iedriver.exe",
```

<br>

Next, go to [Interactive Mode](interactive-mode.html)
