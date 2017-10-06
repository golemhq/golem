Web Drivers
==================================================


### Chrome

To run tests using Chrome, the Chromedriver executable is needed.

ChromeDriver is a standalone server which implements WebDriver's wire protocol for Chromium. ChromeDriver is available for Chrome on Android and Chrome on Desktop (Mac, Linux, Windows and ChromeOS).  

Download Chromedriver from [here](https://sites.google.com/a/chromium.org/chromedriver/)

To set it up for Golem to use, place it anywhere in your machine (you can use the 'drivers' folder that is generated automatically inside the test directory) and point to it with the 'chrome_driver_path' settings variable:

**settings.json**
```
"chromedriver_path": "./drivers/chromedriver",
```

#### Chrome headless

Chrome can run headless, without a GUI. To do this, just set the browser of a test or suite to 'chrome-headless' or 'chrome-remote-headless.
Requirements: chrome 58+, chromedriver 2.32+



### Firefox

Firefox needs the geckodriver to work.

Download the Geckodriver from [here](https://github.com/mozilla/geckodriver/releases)

The Geckodriver should be in the system path. Golem can manually replace this with the following setting variable.

**settings.json**
```
geckodriver_path": "./drivers/geckodriver",
```

Next, go to [Interactive Mode](interactive-mode.html)
