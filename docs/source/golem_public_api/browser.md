Browser Module
==================================================

Functions to manipulate WebDriver Browser instances.

Location: golem.**browser**


## **open_browser**(browser_id=None)

When opening more than one browser instance per test provide a browser_id to switch between browsers later on.

Raises:
  - InvalidBrowserIdError: The browser Id is already in use

Returns: the opened browser

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