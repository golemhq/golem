Interactive Mode
==================================================

With Golem the execution of a test can be paused at any point and start an interactive console that has all the Golem commands at disposal. This is extremely useful when writing and debugging tests.


**Debug action**

To start the interactive console at any point of a test just add the 'debug' action. Example:

**test.py**
```python

def test(data):
    navigate('http://wikipedia.org/')
    debug()
    click(page.button)
    capture('final screenshot')
```

When the test reaches the second step, the interactive console is going to start:


<div class="admonition note">
    <p class="first admonition-title">Note</p>
    <p>It is possible to add folders to the list by appending '/' at the end</p>
</div>

- *implicit_wait*

Default time to wait looking for an element until it is found. Default is 20 seconds.

- *screenshot_on_error*

Take a screenshot on error by default. Default is True.

- *screenshot_on_step*

Take a screenshot on every step. Default is False.

- *default_driver*

Define the driver to use unless overriden by the -d/--driver flag. Default is 'chrome'. Valid options are: firefox, chrome, TBD

- *chrome_driver_path*

Path to the chrome driver executable. By default it points to the *drivers* folder inside the test dir.

- *gecko_driver_path*

Path to the gecko driver executable. By default it points to the *drivers* folder inside the test dir.

- *remote_url*

the URL to use when connecting to a remote webdriver, for example, when using selenium grid. Default is 'http://localhost:4444/wd/hub'

- *wait_hook*

Custom wait method to use for every action, that can be specific to each application. It must be defined inside extend.py

<br>

Next, go to [Web Drivers](web-drivers.html)