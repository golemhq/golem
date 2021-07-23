Browser Module
==================================================

Functions to manipulate WebDriver Browser instances.

Location: golem.**browser**


## **open_browser**(browser_name=None, capabilities=None, remote_url=None, browser_id=None)

When no arguments are provided the browser is selected from the CLI -b|--browsers argument, the suite *browsers* list, or the *default_browser* setting.

This can be overridden in two ways:
- a local webdriver instance or
- a remote Selenium Grid driver instance.

To open a local Webdriver instance pass browser_name with a [valid value](../browsers.html#valid-options)

To open a remote Selenium Grid driver pass a capabilities dictionary and
a remote_url.
The minimum capabilities required is:
```
{
    browserName: 'chrome'
    version: ''
    platform: ''
}
```
More info here: [https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities](https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities)

If remote_url is None it will be taken from the `remote_url` setting.

When opening more than one browser instance per test
provide a browser_id to switch between browsers later on

Returns:
  the opened browser

## **get_browser**()

Returns the active browser. Starts a new one if there is none.

## **activate_browser**(browser_id)

Activate an opened browser.
Only needed when the test starts more than one browser instance.

Raises:
  - InvalidBrowserIdError: The browser Id does not correspond to an opened browser

Returns: the active browser

## **element**(*args, **kwargs)

Shortcut to golem.browser.get_browser().find().

See [find](webdriver-class.html#find-args-kwargs-small-golem-small).

## **elements**(*args, **kwargs)

Shortcut to golem.browser.get_browser().find_all()

See [find_all](webdriver-class.html#find-all-args-kwargs-small-golem-small).