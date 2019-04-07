Using Multiple Browsers Sessions
==================================================

Sometimes a test requires two or more different browser sessions opened at the same time.

A browser is opened by default when using an action that needs a browser.
To open a browser explicitly use the **open_browser** action or *golem.browser.**open_browser()***.

## Open Multiple Browsers

To open a second browser use **open_browser** again and pass an id to identify it.
The first browser has 'main' as its id by default.

The list of opened browsers is stored in golem.execution.browsers.

To use a browser when there is more than one, it has to be activated first:

```python
open_browser()
open_browser('second')
activate_browser('second')
```

As an example, testing a chat application with two concurrent users:

```python
def test(data):
    navigate('https://app-url.com/')  # browser opened with id='main'
    open_browser('second browser')  # second browser opened
    navigate('https://app-url.com/')
    activate_browser('main')
    send_chat_message('hey there!')
    activate_browser('second browser')
    assert_message_received('hey there!')
```