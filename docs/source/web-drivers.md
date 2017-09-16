Web Drivers
==================================================


##### Chrome

To automate Chrome, Chromedriver is needed.

ChromeDriver is a standalone server which implements WebDriver's wire protocol for Chromium. ChromeDriver is available for Chrome on Android and Chrome on Desktop (Mac, Linux, Windows and ChromeOS).  

Download Chromedriver from [here](https://sites.google.com/a/chromium.org/chromedriver/)

To set it up for Golem to use, place it anywhere in your machine (you can use the 'drivers' folder that is generated automatically inside the test directory) and point to it with the 'chrome_driver_path' settings variable:

**settings.json**
```
"chrome_driver_path": "./drivers/chromedriver",
```

## Chrome headless

Chrome can run headless, requirements: chrome 58+, chromedriver 2.32+



##### Firefox

Firefox used to work out of the box without the need of any extra driver server. Starting from Selenium 3.4, the Geckodriver server is required.

Download the Geckodriver from [here](https://github.com/mozilla/geckodriver/releases)

The Geckodriver should be in the system path. Golem can manually replace this with the following setting variable.

**settings.json**
```
gecko_driver_path": "./drivers/geckodriver",
```

<!-- Next, go to [Using Pages](using-pages.html) -->
