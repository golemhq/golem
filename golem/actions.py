"""Golem actions"""
import code
import importlib
import logging
import os
import pdb
import sys
import time
import traceback
import types
import uuid
from contextlib import contextmanager

import requests

from golem import browser, execution, helpers
from golem.core import utils
from golem.test_runner import test_logger
from golem.report import utils as report_utils


def _add_error(message, description='', log_level='ERROR'):
    """Add a new error to execution.errors and log the error"""
    error = {
        'message': message,
        'description': description
    }
    execution.errors.append(error)
    message = f'{message}\n{description}' if description else message
    _log(message, log_level)


def _add_step(message, log_level='INFO', log_step=True):
    """Add a new step to execution.steps and log the step"""
    step = {
        'message': message,
        'screenshot': None,
        'error': None
    }
    execution.steps.append(step)
    if log_step:
        _log(message, log_level)


def _append_error(message, description=''):
    """Append error to last step.
    The last step must not have an error already added."""
    if len(execution.steps) > 0:
        last_step = execution.steps[-1]
        if not last_step['error']:
            last_step['error'] = {
                'message': message,
                'description': description
            }
        else:
            raise Exception('last step already contains an error')
    else:
        raise Exception('there is no last step to append error')


@contextmanager
def _assert_step(step_message, error='', take_screenshots=True):
    """Assert step context manager"""
    _add_step(step_message)
    _run_wait_hook()
    step = types.SimpleNamespace(condition=None, error='')
    yield step
    error_message = error if error else step.error
    assert step.condition, error_message
    if take_screenshots:
        _screenshot_on_step()


def _capture_screenshot(image_name):
    """take a screenshot and store it in execution.test_reportdir.
    test_reportdir must already exist.

    Screenshot format, size and quality can be modified using the
      'screenshots' setting key.
    Pillow must be installed in order to modify the screenshot before saving.
    'screenshots' setting can have the following attributes:
      - format: must be 'PNG' or 'JPEG'
      - quality: must be an int in 1..95 range.
          Default is 75. Only applies to JPEG.
      - width and height: must be int greater than 0
      - resize: must be an int greater than 0.
          Str in the format '55' or '55%' is also allowed.
    """
    if not execution.test_reportdir:
        execution.logger.debug('cannot take screenshot, report directory does not exist')
        return None

    if not execution.settings['screenshots']:
        screenshot_filename = f'{image_name}.png'
        screenshot_path = os.path.join(execution.test_reportdir, screenshot_filename)
        get_browser().get_screenshot_as_file(screenshot_path)
    else:
        screenshot_settings = execution.settings['screenshots']
        format = screenshot_settings.get('format', 'PNG').upper()
        if format == 'JPG':
            format = 'JPEG'
        quality = screenshot_settings.get('quality', None)
        width = screenshot_settings.get('width', None)
        height = screenshot_settings.get('height', None)
        resize = screenshot_settings.get('resize', None)
        screenshot_filename = report_utils.save_screenshot(execution.test_reportdir,
                                                           image_name, format, quality,
                                                           width, height, resize)
    return screenshot_filename


def _generate_screenshot_name(message):
    """Generate a valid filename from a message string"""
    sanitized_filename = utils.get_valid_filename(message)
    random_id = str(uuid.uuid4())[:5]
    return f'{sanitized_filename}_{random_id}'


def _log(message, log_level="INFO"):
    """Log a message"""
    log_level = log_level.upper()
    if log_level in test_logger.VALID_LOG_LEVELS:
        log_level_int = getattr(logging, log_level)
        execution.logger.log(log_level_int, message)
    else:
        raise Exception(f'log level {log_level} is invalid')


def _run_wait_hook():
    wait_hook = execution.settings['wait_hook']
    if wait_hook:
        start_time = time.time()
        extend_module = importlib.import_module(f'projects.{execution.project}.extend')
        wait_hook_function = getattr(extend_module, wait_hook)
        wait_hook_function()
        execution.logger.debug(f'Wait hook waited for {time.time() - start_time} seconds')


def _screenshot_on_condition(condition):
    """Take a screenshot if condition is True
    Append the screenshot to the last step.
    The last step must not have a screenshot already.
    Use the last step message as the screenshot filename.
    """
    if len(execution.steps) > 0:
        try:
            last_step = execution.steps[-1]
            last_screenshot = last_step['screenshot']
            if condition and not last_screenshot:
                last_step_message = last_step['message']
                screenshot_name = _generate_screenshot_name(last_step_message)
                screenshot_filename = _capture_screenshot(screenshot_name)
                last_step['screenshot'] = screenshot_filename
        except Exception as e:
            _log('There was an error while taking screenshot:\n'+traceback.format_exc(), 'WARNING')
    else:
        raise Exception('There is no step to attach the screenshot')


def _screenshot_on_error():
    """Take a screenshot if settings['screenshot_on_error']
    Append the screenshot to the last step.
    The last step must not have a screenshot already.
    Use the last step message as the screenshot filename.
    """
    _screenshot_on_condition(execution.settings['screenshot_on_error'])


def _screenshot_on_step():
    """Take a screenshot if settings['screenshot_on_step']
    Append the screenshot to the last step.
    The last step must not have a screenshot already.
    Use the last step message as the screenshot filename.
    """
    _screenshot_on_condition(execution.settings['screenshot_on_step'])


@contextmanager
def _step(message, run_wait_hook=True, take_screenshots=True):
    """Step context manager (not verify step, not assert step)"""
    _add_step(message)
    if run_wait_hook:
        _run_wait_hook()
    yield
    if take_screenshots:
        _screenshot_on_step()


@contextmanager
def _verify_step(step_message, error='', error_description='', take_screenshots=True):
    """Verify step context manager"""
    _add_step(step_message)
    _run_wait_hook()
    step = types.SimpleNamespace(condition=None, error='', error_description='')
    yield step
    if not step.condition:
        error_message = error if error else step.error
        error_description = error_description if error_description else step.error_description
        _add_error(error_message, error_description)
        _append_error(error_message, error_description)
        if take_screenshots:
            _screenshot_on_error()
    if take_screenshots:
        _screenshot_on_step()


def accept_alert(ignore_not_present=False):
    """Accept an alert, confirm or prompt box.
    Use ignore_not_present to ignore error when alert is not present.

    Parameters:
    ignore_not_present (optional, False) : value"""
    with _step('Accept alert'):
        get_browser().accept_alert(ignore_not_present)


def activate_browser(browser_id):
    """Activates a browser by the browser_id

    When opening more than one browser (not windows or tabs)
    for a single test, the new browser can be assigned to an ID.
    Default browser ID is 'main'.
    Returns the activated browser.

    Parameters:
    browser_id : value
    """
    with _step(f'Activate browser {browser_id}', run_wait_hook=False):
        return browser.activate_browser(browser_id)


def add_cookie(cookie_dict):
    """Add a cookie to the current session.
    
    Required keys are: "name" and "value"
    Optional keys are: "path", "domain", "secure", "expiry"
    
    Note:
    * If a cookie with the same name exists, it will be overridden.
    * This function cannot set the domain of a cookie, the domain URL
    must be visited by the browser first.
    * The domain is set automatically to the current domain the browser is in.
    * If the browser did not visit any URL (initial blank page) this
    function will fail with "Message: unable to set cookie"

    Parameters:
    cookie_dict : value
    """
    execution.logger.info(f'Add cookie: {cookie_dict}')
    get_browser().add_cookie(cookie_dict)


def assert_alert_not_present():
    """Assert an alert is not present"""
    _add_step('Assert an alert is not present')
    _run_wait_hook()
    assert not get_browser().alert_is_present(), 'an alert was present'
    _screenshot_on_step()


def assert_alert_present():
    """Assert an alert is present"""
    _add_step('Assert an alert is present')
    _run_wait_hook()
    assert get_browser().alert_is_present(), 'an alert was not present'
    _screenshot_on_step()


def assert_alert_text(text):
    """Assert alert text
    This will fail if there is no alert present.

    Parameters:
    text : value
    """
    _add_step(f"Assert alert text is '{text}'")
    _run_wait_hook()
    alert_text = get_browser().switch_to.alert.text
    error_msg = f"expected alert text to be '{text}' but was '{alert_text}'"
    assert alert_text == text, error_msg
    _screenshot_on_step()


def assert_alert_text_is_not(text):
    """Assert alert text is not `text`
    This will fail if there is no alert present.

    Parameters:
    text : value
    """
    _add_step(f"Assert alert text is not '{text}'")
    _run_wait_hook()
    alert_text = get_browser().switch_to.alert.text
    error_msg = f"expected alert text not to be '{text}'"
    assert alert_text != text, error_msg
    _screenshot_on_step()


def assert_amount_of_windows(amount):
    """Assert the amount of open windows/tabs

    Parameters:
    amount : value
    """
    _add_step(f'Assert amount of open windows is {amount}')
    _run_wait_hook()
    actual_amount = len(get_window_handles())
    error_msg = f'expected {amount} windows but got {actual_amount}'
    assert actual_amount == amount, error_msg
    _screenshot_on_step()


def assert_cookie_present(name):
    """Assert a cookie exists in the current session.
    The cookie is found by its name.

    Parameters:
    name: value
    """
    _add_step(f"Assert that cookie '{name}' exists")
    _run_wait_hook()
    cookie = browser.get_browser().get_cookie(name)
    assert cookie, f"cookie '{name}' was not found"


def assert_cookie_value(name, value):
    """Assert the value of a cookie.
    This will fail if the cookie does not exist.

    Parameters:
    name: value
    value: value
    """
    _add_step(f"Assert that cookie '{name}' value is '{value}'")
    _run_wait_hook()
    cookie = browser.get_browser().get_cookie(name)
    if not cookie:
        raise Exception(f'Cookie "{name}" was not found')
    elif not 'value' in cookie:
        raise Exception(f'Cookie "{name}" did not have "value" key')
    else:
        msg = f"expected cookie '{name}' value to be '{value}' but was \'{cookie['value']}\'"
        assert cookie['value'] == value, msg


def assert_element_attribute(element, attribute, value):
    """Assert value of element attribute

    Parameters:
    element : element
    attribute : value
    value : value
    """
    element = get_browser().find(element, timeout=0)
    step_message = f"Assert element {element.name} attribute {attribute} value is '{value}'"
    _add_step(step_message)
    _run_wait_hook()
    attr_value = element.get_attribute(attribute)
    msg = f"expected element {element.name} attribute {attribute} value to be " \
          f"'{value}' was '{attr_value}'"
    assert attr_value == value, msg
    _screenshot_on_step()


def assert_element_attribute_is_not(element, attribute, value):
    """Assert the value of element attribute is not `value`

    Parameters:
    element : element
    attribute : value
    value : value
    """
    element = get_browser().find(element, timeout=0)
    step_message = f'Assert element {element.name} attribute {attribute} value is not {value}'
    _add_step(step_message)
    _run_wait_hook()
    attr_value = element.get_attribute(attribute)
    msg = f'expected element {element.name} attribute {attribute} value to not be {value}'
    assert attr_value != value, msg
    _screenshot_on_step()


def assert_element_checked(element):
    """Assert element is checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} is checked')
    _run_wait_hook()
    assert element.is_selected(), f'element {element.name} is not checked'
    _screenshot_on_step()


def assert_element_displayed(element):
    """Assert element is displayed (visible to the user)

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    _add_step(f'Assert element {element.name} is displayed')
    _run_wait_hook()
    assert element.is_displayed(), f'element {element.name} is not displayed'
    _screenshot_on_step()


def assert_element_enabled(element):
    """Assert element is enabled.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} is enabled')
    _run_wait_hook()
    assert element.is_enabled(), f'element {element.name} is not enabled'
    _screenshot_on_step()


def assert_element_has_attribute(element, attribute):
    """Assert element has attribute

    Parameters:
    element : element
    attribute : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} has attribute {attribute}')
    _run_wait_hook()
    error_msg = f'element {element.name} does not have attribute {attribute}'
    assert element.has_attribute(attribute), error_msg
    _screenshot_on_step()


def assert_element_has_focus(element):
    """Assert element has focus

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} has focus')
    _run_wait_hook()
    error_msg = f'element {element.name} does not have focus'
    assert element.has_focus(), error_msg


def assert_element_has_not_attribute(element, attribute):
    """Assert element has not attribute

    Parameters:
    element : element
    attribute : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} has not attribute {attribute}')
    _run_wait_hook()
    error_msg = f'element {element.name} has attribute {attribute}'
    assert not element.has_attribute(attribute), error_msg


def assert_element_has_not_focus(element):
    """Assert element does not have focus

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} does not have focus')
    _run_wait_hook()
    error_msg = f'element {element.name} has focus'
    assert not element.has_focus(), error_msg


def assert_element_not_checked(element):
    """Assert element is not checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    element = browser.get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} is not checked')
    _run_wait_hook()
    assert not element.is_selected(), f'element {element.name} is checked'
    _screenshot_on_step()


def assert_element_not_displayed(element):
    """Assert element is not displayed (visible to the user)

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    _add_step(f'Assert element {element.name} is not displayed')
    _run_wait_hook()
    assert not element.is_displayed(), f'element {element.name} is displayed'
    _screenshot_on_step()


def assert_element_not_enabled(element):
    """Assert element is not enabled.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f'Assert element {element.name} is not enabled')
    _run_wait_hook()
    assert not element.is_enabled(), f'element {element.name} is enabled'
    _screenshot_on_step()


def assert_element_not_present(element):
    """Assert element is not present in the DOM

    Parameters:
    element : element
    """
    _add_step('Assert element is not present')
    _run_wait_hook()
    assert not get_browser().element_is_present(element), f'element {element} is present'


def assert_element_present(element):
    """Assert element is present in the DOM

    Parameters:
    element : element
    """
    _add_step('Assert element is present')
    _run_wait_hook()
    assert get_browser().element_is_present(element), f'element {element} is not present'


def assert_element_text(element, text):
    """Assert the text of the element

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} text is '{text}'")
    _run_wait_hook()
    msg = f"expected element {element.name} text to be '{text}' but was '{element.text}'"
    assert element.text == text, msg
    _screenshot_on_step()


def assert_element_text_contains(element, text):
    """Assert element contains text

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} contains text '{text}'")
    _run_wait_hook()
    msg = f"expected element {element.name} text '{element.text}' to contain '{text}'"
    assert text in element.text, msg
    _screenshot_on_step()


def assert_element_text_is_not(element, text):
    """Assert the text of the element is not `text`

    Parameters:
    element : element
    text : value
    """
    element = browser.get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} text is not '{text}'")
    _run_wait_hook()
    msg = f"expected element {element.name} text to not be '{text}'"
    assert element.text != text, msg
    _screenshot_on_step()


def assert_element_text_not_contains(element, text):
    """Assert the text of the element does not contain `text`

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} does not contain text '{text}'")
    _run_wait_hook()
    msg = f"element {element.name} text '{element.text}' contains text '{text}'"
    assert text not in element.text, msg
    _screenshot_on_step()


def assert_element_value(element, value):
    """Assert element value

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} value is '{value}'")
    _run_wait_hook()
    element_value = element.value
    msg = f"expected element {element.name} value to be '{value}' but was '{element_value}'"
    assert element_value == value, msg
    _screenshot_on_step()


def assert_element_value_is_not(element, value):
    """Assert element value is not `value`

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element, timeout=0)
    _add_step(f"Assert element {element.name} value is not '{value}'")
    _run_wait_hook()
    element_value = element.value
    msg = f"expected element {element.name} value to not be '{value}'"
    assert element_value != value, msg
    _screenshot_on_step()


def assert_page_contains_text(text):
    """Assert the given text is present anywhere in the page source

    Parameters:
    text : value
    """
    _add_step(f"Assert '{text}' is present in the page")
    _run_wait_hook()
    assert text in get_browser().page_source, f"text '{text}' not found in the page"
    _screenshot_on_step()


def assert_page_not_contains_text(text):
    """Assert the given text is not present anywhere in the page source

    Parameters:
    text : value
    """
    _add_step(f"Assert '{text}' is not present in the page")
    _run_wait_hook()
    assert text not in get_browser().page_source, f"text '{text}' was found in the page"
    _screenshot_on_step()


def assert_response_status_code(response, status_code):
    """Assert the response status code.

    Parameters:
    response : value
    status_code : value
    """
    if isinstance(status_code, str):
        if status_code.isdigit():
            status_code = int(status_code)
    _add_step(f'Assert response status code is {status_code}')
    msg = f'expected response status code to be {status_code} but was {response.status_code}'
    assert response.status_code == status_code, msg


def assert_selected_option_by_text(element, text):
    """Assert an element has a selected option by the option text

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element)
    _add_step(f"Assert selected option text of element {element.name} is '{text}'")
    _run_wait_hook()
    selected_option_text = element.select.first_selected_option.text
    error_msg = f"expected selected option in element {element.name} to be '{text}' " \
                f"but was '{selected_option_text}'"
    assert selected_option_text == text, error_msg
    _screenshot_on_step()


def assert_selected_option_by_value(element, value):
    """Assert an element has a selected option by the option value

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element)
    _add_step(f'Assert selected option value of element {element.name} is {value}')
    _run_wait_hook()
    selected_option_value = element.select.first_selected_option.value
    error_msg = f'expected selected option in element {element.name} to be {value} ' \
                f'but was {selected_option_value}'
    assert selected_option_value == value, error_msg
    _screenshot_on_step()


def assert_title(title):
    """Assert the page title

    Parameters:
    title : value
    """
    _add_step(f"Assert page title is '{title}'")
    _run_wait_hook()
    error_msg = f"expected title to be '{title}' but was '{get_browser().title}'"
    assert get_browser().title == title, error_msg
    _screenshot_on_step()


def assert_title_contains(partial_title):
    """Assert the page title contains partial_title

    Parameters:
    partial_title : value
    """
    _add_step(f"Assert page title contains '{partial_title}'")
    _run_wait_hook()
    error_msg = f"expected title to contain '{partial_title}'"
    assert partial_title in get_browser().title, error_msg
    _screenshot_on_step()


def assert_title_is_not(title):
    """Assert the page title is not the given value

    Parameters:
    title : value
    """
    _add_step(f"Assert page title is not '{title}'")
    _run_wait_hook()
    assert get_browser().title != title, f"expected title to not be '{title}'"
    _screenshot_on_step()


def assert_title_not_contains(text):
    """Assert the page title does not contain text

    Parameters:
    text : value
    """
    _add_step(f"Assert page title does not contain '{text}'")
    _run_wait_hook()
    assert text not in get_browser().title, f"title contains '{text}'"
    _screenshot_on_step()


def assert_url(url):
    """Assert the current URL

    Parameters:
    url : value
    """
    _add_step(f"Assert URL is '{url}'")
    _run_wait_hook()
    error_msg = f"expected URL to be '{url}' but was '{get_browser().current_url}'"
    assert get_browser().current_url == url, error_msg
    _screenshot_on_step()


def assert_url_contains(partial_url):
    """Assert the current URL contains partial_url

    Parameters:
    partial_url : value
    """
    _add_step(f"Assert URL contains '{partial_url}'")
    _run_wait_hook()
    error_msg = f"expected URL to contain '{partial_url}'"
    assert partial_url in get_browser().current_url, error_msg
    _screenshot_on_step()


def assert_url_is_not(url):
    """Assert the current URL is not `url`

    Parameters:
    url : value
    """
    _add_step(f"Assert URL is not '{url}'")
    _run_wait_hook()
    assert get_browser().current_url != url, f"expected URL to not be '{url}'"
    _screenshot_on_step()


def assert_url_not_contains(partial_url):
    """Assert the current URL does not contain partial_url

    Parameters:
    partial_url : value
    """
    _add_step(f"Assert page title does not contain '{partial_url}'")
    _run_wait_hook()
    actual_url = get_browser().current_url
    error_msg = f"expected URL '{actual_url}' to not contain '{partial_url}'"
    assert partial_url not in actual_url, error_msg
    _screenshot_on_step()


def assert_window_present_by_partial_title(partial_title):
    """Assert there is a window/tab present by partial title

    Parameters:
    partial_title : value
    """
    _add_step(f"Assert window present by partial title '{partial_title}'")
    _run_wait_hook()
    error_msg = f"There is no window present with partial title '{partial_title}'"
    window_titles = get_browser().get_window_titles()
    assert any(partial_title in t for t in window_titles), error_msg
    _screenshot_on_step()


def assert_window_present_by_partial_url(partial_url):
    """Assert there is a window/tab present by partial URL

    Parameters:
    partial_url : value
    """
    _add_step(f"Assert window present by partial URL '{partial_url}'")
    _run_wait_hook()
    urls = get_browser().get_window_urls()
    error_msg = f"There is no window present with partial URL '{partial_url}'"
    assert any(partial_url in url for url in urls), error_msg
    _screenshot_on_step()


def assert_window_present_by_title(title):
    """Assert there is a window/tab present by title

    Parameters:
    title : value
    """
    _add_step(f"Assert window present by title '{title}'")
    _run_wait_hook()
    error_msg = f"There is no window present with title '{title}'"
    assert title in get_browser().get_window_titles(), error_msg
    _screenshot_on_step()


def assert_window_present_by_url(url):
    """Assert there is a window/tab present by URL

    Parameters:
    url : value
    """
    _add_step(f"Assert window present by URL '{url}'")
    _run_wait_hook()
    error_msg = f"There is no window present with URL '{url}'"
    assert url in get_browser().get_window_urls(), error_msg
    _screenshot_on_step()


def check_element(element):
    """Check an element (checkbox or radiobutton).
    If element is already checked this is is ignored.

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f'Check element {element.name}'):
        get_browser().check_element(element)


def clear_element(element):
    """Clear an element (e.g. a text input)

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f'Clear element {element.name}'):
        element.clear()


def click(element):
    """Click element

    Parameters:
    element : element
    """
    element = browser.get_browser().find(element)
    with _step(f'Click {element.name}'):
        element.click()


def close_browser():
    """Close browser and all it's windows/tabs"""
    execution.logger.info('Close browser')
    get_browser().quit()
    execution.browser = None


def close_window():
    """Close current window/tab.
    If there is only one window, this will close the browser as well.
    If there are other windows open, this will try to switch to
    the first window afterwards.
    """
    with _step('Close current window'):
        browser_ = get_browser()
        browser_.close()
        if browser_.window_handles:
            browser_.switch_to_first_window()


def close_window_by_index(index):
    """Close window/tab by index.
    Note: "The order in which the window handles are returned is arbitrary."

    Parameters:
    index : value
    """
    with _step(f'Close window by index {index}'):
        get_browser().close_window_by_index(index)


def close_window_by_partial_title(partial_title):
    """Close window/tab by partial title

    Parameters:
    partial_title : value
    """
    with _step(f"Close window by partial title '{partial_title}'"):
        get_browser().close_window_by_partial_title(partial_title)


def close_window_by_partial_url(partial_url):
    """Close window/tab by partial URL

    Parameters:
    partial_title : value
    """
    with _step(f"Close window by partial URL '{partial_url}'"):
        get_browser().close_window_by_partial_url(partial_url)


def close_window_by_title(title):
    """Close window/tab by title

    Parameters:
    title : value
    """
    with _step(f"Close window by title '{title}'"):
        get_browser().close_window_by_title(title)


def close_window_by_url(url):
    """Close window/tab by URL

    Parameters:
    url : value
    """
    with _step(f"Close window by URL '{url}'"):
        get_browser().close_window_by_url(url)


def delete_all_cookies():
    """Delete all cookies from the current session.
    Note: this only deletes cookies from the current domain.
    """
    with _step('Delete all cookies'):
        get_browser().delete_all_cookies()


def delete_cookie(name):
    """Delete a cookie from the current session

    Parameters:
    name: value
    """
    with _step(f"Delete cookie '{name}'"):
        cookie = get_browser().get_cookie(name)
        if not cookie:
            raise Exception(f"Cookie '{name}' was not found")
        else:
            get_browser().delete_cookie(name)


def dismiss_alert(ignore_not_present=False):
    """Dismiss an alert.
     Use ignore_not_present to ignore error when alert is not present.

    Parameters:
    ignore_not_present (False) : value"""
    with _step('Dismiss alert'):
        get_browser().dismiss_alert(ignore_not_present)


def double_click(element):
    """Double click an element

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f'Double click element {element.name}'):
        element.double_click()


# TODO
# def drag_and_drop(element, target):
#     """Drag and drop an element into target
#     Parameters:
#     element : element
#     target : element
#     """
#     b = get_browser()
#     element = b.find(element)
#     target = b.find(target)
#     step_message = 'Drag and drop {} into {}'.format(element.name, target.name)
#     execution.logger.info(step_message)
#     _add_step(step_message)
#     b.drag_and_drop(element, target)
#     _screenshot_on_step()


def error(message, description=''):
    """Add an error to the test.
    The test will continue.

    Parameters:
    message : value
    description (optional) : value
    """
    _add_step('ERROR', log_step=False)
    _add_error(message, description)
    _append_error(message, description)
    if execution.browser:
        _screenshot_on_error()


def execute_javascript(script, *args):
    """Execute javascript code.
    The result is returned.

    Parameters:
    script : value
    *args : value
    """
    _add_step(f"Execute javascript code '{script}' with args '{args}'")
    return get_browser().execute_script(script, *args)


def fail(message=''):
    """Mark the test as failure and stop

    Parameters:
    message (optional, '') : value
    """
    raise AssertionError(message)


def focus_element(element):
    """Give focus to element

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f'Focus element {element.name}'):
        element.focus()


def get(url):
    """Navigate to the given URL

    Parameters:
    url : value
    """
    navigate(url)


def get_active_element():
    """Returns the element with focus, or BODY if nothing has focus"""
    execution.logger.debug('Get active element')
    return get_browser().switch_to.active_element


def get_alert_text():
    """Get alert text"""
    execution.logger.debug('get alert text')
    return get_browser().switch_to.alert.text


def get_browser():
    """Get the current active browser"""
    return browser.get_browser()


def get_cookie(name):
    """Get a cookie by its name.
    Returns the cookie if found, None if not.

    Parameters:
    name : value
    """
    execution.logger.debug(f"Get cookie '{name}'")
    return get_browser().get_cookie(name)


def get_cookies():
    """Returns a list of dictionaries, corresponding to cookies
    present in the current session.
    """
    execution.logger.debug('Get all cookies')
    return get_browser().get_cookies()


def get_current_url():
    """Return the current browser URL"""
    return get_browser().current_url


def get_data():
    """Return test data"""
    return execution.data


def get_secrets():
    """Return secrets"""
    return execution.secrets


def get_element_attribute(element, attribute):
    """Get the attribute value of element.
    If the attribute is not present in element, None is returned.

    Parameters:
    element : element
    attribute : value
    """
    element = get_browser().find(element)
    execution.logger.debug(f"Get '{element}' element '{attribute}' attribute")
    return element.get_attribute(attribute)


def get_element_text(element):
    """Get the element text

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    execution.logger.debug(f"Get '{element}' element text")
    return element.text


def get_element_value(element):
    """Get the element value attribute

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    execution.logger.debug(f"Get '{element}' element value")
    return element.value


def get_page_source():
    """Get the page source"""
    execution.logger.debug('Get page source')
    return get_browser().page_source


def get_search_timeout():
    """Get search timeout"""
    execution.logger.debug('Get search timeout')
    return execution.settings['search_timeout']


def get_window_handle():
    """Get current window handle"""
    execution.logger.debug('Get current window handle')
    return get_browser().current_window_handle


def get_window_handles():
    """Return a list with the handles of all the open windows/tabs"""
    execution.logger.debug('Get all window handles')
    return get_browser().window_handles


def get_window_index():
    """"Get the index of the current window/tab from the
    list of window handles"""
    execution.logger.debug('Get current window index')
    return get_browser().get_window_index()


def get_window_size():
    """Return the window size with the following format:
    size = {
        'width': x,
        'height': y
    }
    """
    return get_browser().get_window_size()


def get_window_title():
    """Get window title"""
    execution.logger.debug('Get window title')
    return get_browser().title


def get_window_titles():
    """Return a list with the titles of all the open windows/tabs"""
    execution.logger.debug('Get window titles')
    return get_browser().get_window_titles()


def go_back():
    """Goes one step backward in the browser history"""
    with _step('Go back'):
        get_browser().back()


def go_forward():
    """Goes one step forward in the browser history"""
    with _step('Go forward'):
        get_browser().forward()


def highlight_element(element):
    """Highlight element on the page

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    element.highlight()


def http_get(url, headers={}, params={}, verify_ssl_cert=True):
    """Perform an HTTP GET request to the given URL.
    Headers and params are optional dictionaries.
    Store response in data.last_response
    Returns the response

    Parameters:
    url : value
    headers (optional, dict) : value
    params (optional, dict) : value
    verify_ssl_cert (optional, True) : value
    """
    _add_step(f'Make a GET request to {url}')
    response = requests.get(url, headers=headers, params=params,
                            verify=verify_ssl_cert)
    store('last_response', response)
    return response


def http_post(url, headers={}, data={}, verify_ssl_cert=True):
    """Perform an HTTP POST request to the given URL.
    Headers and data are optional dictionaries.
    Stores the response in data.last_response
    Returns the response

    Parameters:
    url : value
    headers (optional, dict) : value
    data (optional, dict) : value
    verify_ssl_cert (optional, default is True) : value
    """
    _add_step(f'Make a POST request to {url}')
    response = requests.post(url, headers=headers, data=data,
                             verify=verify_ssl_cert)
    store('last_response', response)
    return response


def interactive_mode():
    """Enter interactive mode.
    The test needs to be run with -i flag, otherwise this is ignored.
    """
    if not execution.settings['interactive']:
        execution.logger.info('the -i flag is required to access interactive mode')
        return
    try:
        # optional, enables Up/Down/History in the console
        # not available in windows
        import readline
    except:
        pass

    def console_exit():
        raise SystemExit

    def console_help():
        msg = ('# start a browser and find an element:\n'
               'navigate(\'http://..\')\n'
               'browser = get_browser()\n'
               'browser.title\n'
               'element = browser.find(id=\'some-id\')\n'
               'element.text\n'
               '\n'
               '# use Golem actions\n'
               'actions.send_keys(element, \'some text\')\n'
               '\n'
               '# import a page from a project\n'
               'from projects.project_name.pages import page_name\n'
               '\n'
               '# get test data (when run from a test)\n'
               'execution.data')
        print(msg)

    vars_copy = globals().copy()
    vars_copy.update(locals())
    vars_copy['exit'] = console_exit
    vars_copy['help'] = console_help
    actions_module = sys.modules[__name__]
    vars_copy['actions'] = actions_module
    banner = ('Entering interactive mode\n'
              'type exit() to stop\n'
              'type help() for more info')
    shell = code.InteractiveConsole(vars_copy)
    try:
        shell.interact(banner=banner)
    except SystemExit:
        pass


def javascript_click(element):
    """Click an element using Javascript
    
    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f'Javascript click element {element.name}'):
        element.javascript_click()


def log(message, level="INFO"):
    """Log a message.
    Valid log levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL

    Parameters:
    message : value
    level (optional, 'INFO') : value
    """
    _log(message, level)


def maximize_window():
    """Maximize browser window"""
    execution.logger.debug('maximize browser window')
    get_browser().maximize_window()


def mouse_over(element):
    """Perform a mouse over on element

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    with _step(f"Mouse over element '{element.name}'"):
        element.mouse_over()


def navigate(url):
    """Navigate to a URL

    Parameters:
    url : value
    """
    with _step(f"Navigate to: '{url}'", run_wait_hook=False):
        get_browser().get(url)


def open_browser(browser_name=None, capabilities=None, remote_url=None, browser_id=None):
    """Open a new browser.
    When no arguments are provided the browser is selected from
    the CLI -b|--browsers argument, the suite `browsers` list,
    or the `default_browser` setting.

    This can be overridden in two ways:
    - a local webdriver instance or
    - a remote Selenium Grid driver instance.

    To open a local Webdriver instance pass browser_name with a valid value:
    chrome, chrome-remote, chrome-headless, chrome-remote-headless, edge,
    edge-remote, firefox, firefox-headless, firefox-remote,
    firefox-remote-headless, ie, ie-remote, opera, opera-remote

    To open a remote Selenium Grid driver pass a capabilities dictionary and
    a remote_url.
    The minimum capabilities required is: {
        browserName: 'chrome'
        version: ''
        platform: ''
    }
    More info here: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities
    If remote_url is None it will be taken from the `remote_url` setting.

    browser_id is optional and only used to manage more than one browser for
    the same test. Default browser ID is 'main'.

    Returns the opened browser.

    Parameters:
    browser_name (optional) : value
    capabilities (optional) : value
    remote_url (optional) : value
    browser_id (optional) : value
    """
    with _step('Open browser', take_screenshots=False, run_wait_hook=False):
        return browser.open_browser(browser_name, capabilities, remote_url, browser_id)

    
def press_key(element, key):
    """Press a given key in element.

    Parameters:
    element : element
    key : value
    """
    element = get_browser().find(element)
    with _step(f"Press key: '{key}' in element {element.name}"):
        element.press_key(key)


def random_float(min=1.0, max=100.0, decimals=None):
    """Generate a random float between min and max.

    `decimals` is the maximum amount of decimal places
    the generated float should have.

    Parameters:
    min (optional, 1.0) : value
    max (optional, 100.0) : value
    decimals (optional, None) : value
    """
    randfloat = helpers.random_float(min, max, decimals)
    execution.logger.debug(f'Random float generated: {randfloat}')
    return randfloat


def random_int(min=1, max=100):
    """Generate a random integer between min and max

    Parameters:
    min (optional, 1) : value
    max (optional, 100) : value
    """
    randint = helpers.random_int(min, max)
    execution.logger.debug(f'Random int generated: {randint}')
    return randint


def random_str(length=10, sample=None, prefix='', suffix=''):
    """Generate a random string

    Sample should be a string or a list of strings/characters to
    choose from. The default sample is lowercase ascii letters.
    A few presets can be used:
     - 'LOWERCASE': lower case ascii letters
     - 'UPPERCASE': uppercase ascii letters
     - 'DIGITS': digit characters
     - 'SPECIAL': Special characters
    Example:
     random_str(sample=['LOWERCASE', '!@#$%'])

    prefix: A string to be prepended to the generated string

    suffix: A string to be appended to the generated string

    Parameters:
    length (optional, 10) : value
    sample (optional, None) : value
    prefix (optional, '') : value
    suffix (optional, '') : value
    """
    random_string = helpers.random_str(length, sample, prefix, suffix)
    execution.logger.debug(f'Random string generated: {random_string}')
    return random_string


def refresh_page():
    """Refresh the page"""
    with _step('Refresh page'):
        get_browser().refresh()


def select_option_by_index(element, index):
    """Select an option from a select dropdown by index.

    Parameters:
    element : element
    index : value
    """
    element = get_browser().find(element)
    with _step(f'Select option of index {index} from element {element.name}'):
        element.select.select_by_index(index)


def select_option_by_text(element, text):
    """Select an option from a select dropdown by text.

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element)
    with _step(f"Select option '{text}' from element {element.name}"):
        element.select.select_by_visible_text(text)


def select_option_by_value(element, value):
    """Select an option from a select dropdown by value.

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element)
    with _step(f"Select option of value '{value}' from element {element.name}"):
        element.select.select_by_value(value)


def send_secure_keys(element, text):
    """Send keys to element.
    Text is hidden from logs and report (masked by asterisks).

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element)
    hidden_text = len(text)*'*'
    with _step(f"Write '{hidden_text}' in element {element.name}"):
        element.send_keys(text)


def send_keys(element, text):
    """Send keys to element.

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element)
    with _step(f"Write '{text}' in element {element.name}"):
        element.send_keys(text)


def send_keys_with_delay(element, text, delay=0.1):
    """Send keys to element one by one with a delay between keys.
    Delay must be a positive int or float.

    Parameters:
    element : element
    text : value
    delay (optional, 0.1) : value
    """
    element = get_browser().find(element)
    with _step(f"Write '{text}' in element {element.name} with delay"):
        element.send_keys_with_delay(text, delay)


def send_text_to_alert(text):
    """Send text to an alert

    Parameters:
    text : value
    """
    with _step(f"Send '{text}' to alert"):
        get_browser().switch_to.alert.send_keys(text)


def set_browser_capability(capability_key, capability_value):
    """Set a browser capability.
    Call this action before starting the browser for the
    capability to take effect.

    Parameters:
    capability_key : value
    capability_value : value
    """
    step_message = f"Set browser capability '{capability_key}' to '{capability_value}'"
    execution.logger.debug(step_message)
    execution.browser_definition['capabilities'][capability_key] = capability_value


def set_search_timeout(timeout):
    """Set the search timeout value (in seconds)

    Parameters:
    timeout : value
    """
    execution.logger.debug(f'Set search_timeout to: {timeout}')
    if not isinstance(timeout, int) and not isinstance(timeout, float):
        raise ValueError('timeout must be int or float')
    else:
        execution.settings['search_timeout'] = timeout


def set_trace():
    """Set trace for Python pdb.
    The test needs to be run with -i flag, otherwise this is ignored.
    """
    if not execution.settings['interactive']:
        execution.logger.info('the -i flag is required to set_trace')
        return
    pdb.set_trace()


def set_window_size(width, height):
    """Set the browser window size.

    Parameters:
    width : value
    height : value
    """
    step_message = f'Set browser window size to {width}x, {height}y.'
    execution.logger.debug(step_message)
    get_browser().set_window_size(width, height)


def step(message):
    """Add a step to the report.

    Parameters:
    message : value
    """
    _add_step(message)


def store(key, value):
    """Store a value in data

    Parameters:
    key : value
    value : value
    """
    execution.logger.info(f"Store value '{value}' in key '{key}'")
    setattr(execution.data, key, value)


def store_secret(key, value):
    """Store a key value pair into secrets

    Parameters:
    key : value
    value : value
    """
    execution.logger.info("Stored a key and value into secrets")
    setattr(execution.secrets, key, value)


def submit_form(form_element):
    """Submit form.
    Element can be the form itself or any child element.

    Parameters:
    form_element : element
    """
    with _step('Submit form'):
        get_browser().find(form_element).submit()


def submit_prompt_alert(text):
    """Send text to a prompt alert and accept it.
    If there is no prompt alert present this will fail.

    Parameters:
    text : value
    """
    with _step(f"Submit alert with text '{text}'"):
        get_browser().switch_to.alert.send_keys(text)
        get_browser().switch_to.alert.accept()


def switch_to_default_content():
    """Switch to default content (default frame)"""
    with _step('Switch to default content', take_screenshots=False):
        get_browser().switch_to.default_content()


def switch_to_first_window():
    """Switch to first window/tab"""
    with _step('Switch to first window'):
        get_browser().switch_to_first_window()


def switch_to_frame(frame):
    """Switch to frame.
    frame must be the index, name, or the frame webelement itself.

    Parameters:
    frame : value
    """
    with _step(f'Switch to frame {frame}', take_screenshots=False):
        get_browser().switch_to.frame(frame)


def switch_to_last_window():
    """Switch to last window/tab"""
    with _step('Switch to last window'):
        get_browser().switch_to_last_window()


def switch_to_next_window():
    """Switch to next window/tab in the list of window handles.
    If current window is the last in the list of window handles this
    will circle back from the start.
    """
    with _step('Switch to next window'):
        get_browser().switch_to_next_window()


def switch_to_parent_frame():
    """Switch to the parent of the current frame"""
    with _step('Switch to parent frame', take_screenshots=False):
        get_browser().switch_to.parent_frame()


def switch_to_previous_window():
    """Switch to previous window/tab in the list of window handles.
    If current window is the first in the list of window handles this
    will circle back from the top.
    """
    with _step('Switch to previous window'):
        get_browser().switch_to_previous_window()


def switch_to_window_by_index(index):
    """Switch to window/tab by index.
    Note: "The order in which the window handles are returned is arbitrary."

    Parameters:
    index : value
    """
    with _step(f'Switch to window of index {index}'):
        get_browser().switch_to_window_by_index(index)


def switch_to_window_by_partial_title(partial_title):
    """Switch to window/tab by partial title

    Parameters:
    partial_title : value
    """
    with _step(f"Switch to window with partial title '{partial_title}'"):
        get_browser().switch_to_window_by_partial_title(partial_title)


def switch_to_window_by_partial_url(partial_url):
    """Switch to window/tab by partial URL

    Parameters:
    partial_url : value
    """
    with _step(f"Switch to window with partial URL '{partial_url}'"):
        get_browser().switch_to_window_by_partial_url(partial_url)


def switch_to_window_by_title(title):
    """Switch to window/tab by title

    Parameters:
    title : value
    """
    with _step(f"Switch to window with title '{title}'"):
        get_browser().switch_to_window_by_title(title)


def switch_to_window_by_url(url):
    """Switch to window/tab by URL

    Parameters:
    url : value
    """
    with _step(f"Switch to window with URL '{url}'"):
        get_browser().switch_to_window_by_url(url)


def take_screenshot(message='Screenshot'):
    """Take a screenshot
    `message` will be used for the filename

    Parameters:
    message (optional, 'Screenshot') : value
    """
    try:
        screenshot_name = _generate_screenshot_name(message)
        screenshot_filename = _capture_screenshot(screenshot_name)
        _add_step(message)
        last_step = execution.steps[-1]
        last_step['screenshot'] = screenshot_filename
    except Exception as e:
        _log('There was an error while taking screenshot:\n' + traceback.format_exc(), 'WARNING')


def timer_start(timer_name=''):
    """Start a timer.
    By default start a timer with empty name.
    Use actions.timer_stop() to stop the timer.
    Returns: the current time

    Parameters:
    timer_name (optional) : value
    """
    current_time = None
    if timer_name in execution.timers:
        execution.logger.debug(f"timer '{timer_name}' has already been started")
    else:
        execution.timers[timer_name] = time.time()
    return current_time


def timer_stop(timer_name=''):
    """Stop a timer by its name.
    By default stops a timer with empty name.
    Returns: the elapsed time

    Parameters:
    timer_name (optional) : value
    """
    elapsed_time = None
    if timer_name in execution.timers:
        elapsed_time = round(time.time() - execution.timers[timer_name], 4)
        execution.logger.debug(f'timer {timer_name} stopped: {elapsed_time}')
    else:
        execution.logger.debug(f'timer {timer_name} has not been started')
    return elapsed_time


def uncheck_element(checkbox):
    """Uncheck a checkbox element
    If checkbox is already unchecked this is is ignored.

    Parameters:
    checkbox : element
    """
    element = get_browser().find(checkbox)
    with _step(f'Uncheck checkbox {element.name}'):
        get_browser().uncheck_element(element)


def verify_alert_not_present():
    """Verify an alert is not present"""
    with _verify_step('Verify an alert is not present', 'an alert was present') as s:
        s.condition = not get_browser().alert_is_present()


def verify_alert_present():
    """Verify an alert is present"""
    with _verify_step('Verify an alert is present', 'an alert was not present') as s:
        s.condition = get_browser().alert_is_present()


def verify_alert_text(text):
    """Verify alert text.
    This will fail if there is no alert present.

    Parameters:
    text : value
    """
    with _verify_step(f"Verify alert text is '{text}'") as s:
        alert_text = get_browser().switch_to.alert.text
        s.error = f"Expected alert text to be '{text}' but was '{alert_text}'"
        s.condition = alert_text == text


def verify_alert_text_is_not(text):
    """Verify alert text is not `text`
    This will fail if there is no alert present.

    Parameters:
    text : value
    """
    with _verify_step(f"Verify alert text is not '{text}'") as s:
        alert_text = get_browser().switch_to.alert.text
        s.error = f"Expected alert text not to be '{text}'"
        s.condition = alert_text != text


def verify_amount_of_windows(amount):
    """Verify the amount of open windows/tabs

    Parameters:
    amount : value
    """
    with _verify_step(f'Verify amount of open windows is {amount}') as s:
        actual_amount = len(get_window_handles())
        s.error = f'Expected {amount} windows but got {actual_amount}'
        s.condition = actual_amount == amount


def verify_cookie_present(name):
    """Verify a cookie exists in the current session.
    The cookie is found by its name.

    Parameters:
    name: value
    """
    with _verify_step(f"Verify that cookie '{name}' exists", take_screenshots=False) as s:
        s.error = f"Cookie '{name}' was not found"
        s.condition = browser.get_browser().get_cookie(name)


def verify_cookie_value(name, value):
    """Verify the value of a cookie.
    This will fail if the cookie does not exist.

    Parameters:
    name: value
    value: value
    """
    message = f"Verify that cookie '{name}' value is '{value}'"
    with _verify_step(message, take_screenshots=False) as s:
        cookie = browser.get_browser().get_cookie(name)
        s.error = f"Expected cookie '{name}' value to be '{value}' but was \'{cookie['value']}\'"
        if not cookie:
            raise Exception(f"Cookie '{name}' was not found")
        elif not 'value' in cookie:
            raise Exception(f"Cookie '{name}' did not have 'value' key")
        s.condition = cookie['value'] == value


def verify_element_attribute(element, attribute, value):
    """Verify value of element attribute

    Parameters:
    element : element
    attribute : value
    value : value
    """
    element = get_browser().find(element, timeout=0)
    message = f"Verify element {element.name} attribute {attribute} value is '{value}'"
    with _verify_step(message) as s:
        actual_value = element.get_attribute(attribute)
        s.error = f"expected element {element.name} attribute {attribute} to be " \
                  f"'{value}' but was '{actual_value}'"
        s.condition = actual_value == value


def verify_element_attribute_is_not(element, attribute, value):
    """Verify the value of element attribute is not `value`

    Parameters:
    element : element
    attribute : value
    value : value
    """
    element = get_browser().find(element, timeout=0)
    message = f"Verify element {element.name} attribute {attribute} value is not '{value}'"
    with _verify_step(message) as s:
        actual_value = element.get_attribute(attribute)
        s.error = f"expected element {element.name} attribute {attribute} to not be '{value}'"
        s.condition = actual_value != value


def verify_element_checked(element):
    """Verify element is checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} is checked') as s:
        s.error = f'element {element.name} is not checked'
        s.condition = element.is_selected()


def verify_element_displayed(element):
    """Verify element is displayed (visible to the user)

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    with _verify_step(f'Verify element {element.name} is displayed') as s:
        s.error = f'element {element.name} is not displayed'
        s.condition = element.is_displayed()


def verify_element_enabled(element):
    """Verify element is enabled.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} is enabled') as s:
        s.error = f'element {element.name} is not enabled'
        s.condition = element.is_enabled()


def verify_element_has_attribute(element, attribute):
    """Verify element has attribute

    Parameters:
    element : element
    attribute : value
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} has attribute {attribute}') as s:
        s.error = f'element {element.name} does not have attribute {attribute}'
        s.condition = element.has_attribute(attribute)


def verify_element_has_focus(element):
    """Verify element has focus

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} has focus') as s:
        s.error = f'element {element.name} does not have focus'
        s.condition = element.has_focus()


def verify_element_has_not_attribute(element, attribute):
    """Verify element has not attribute

    Parameters:
    element : element
    attribute : value
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} has not attribute {attribute}') as s:
        s.error = f'element {element.name} has attribute {attribute}'
        s.condition = not element.has_attribute(attribute)


def verify_element_has_not_focus(element):
    """Verify element does not have focus

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} does not have focus') as s:
        s.error = f'element {element.name} has focus'
        s.condition = not element.has_focus()


def verify_element_not_checked(element):
    """Verify element is not checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    element = browser.get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} is not checked') as s:
        s.error = f'element {element.name} is checked'
        s.condition = not element.is_selected()


def verify_element_not_displayed(element):
    """Verify element is not displayed (visible to the user)

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    with _verify_step(f'Verify element {element.name} is not displayed') as s:
        s.error = f'element {element.name} is displayed'
        s.condition = not element.is_displayed()


def verify_element_not_enabled(element):
    """Verify element is not enabled.

    Parameters:
    element : element
    """
    element = get_browser().find(element, timeout=0)
    with _verify_step(f'Verify element {element.name} is not enabled') as s:
        s.error = f'Element {element.name} is enabled'
        s.condition = not element.is_enabled()


def verify_element_not_present(element):
    """Verify element is not present in the DOM

    Parameters:
    element : element
    """
    with _verify_step(f'Verify element {element} is not present') as s:
        s.error = f'element {element} is present'
        s.condition = not get_browser().element_is_present(element)


def verify_element_present(element):
    """Verify element is present in the DOM

    Parameters:
    element : element
    """
    with _verify_step(f'Verify element {element} is present') as s:
        s.error = f'element {element} is not present'
        s.condition = get_browser().element_is_present(element)


def verify_element_text(element, text):
    """Verify the text of the element

    Parameters:
    element : element
    text : value
    """
    element = browser.get_browser().find(element, timeout=0)
    with _verify_step(f"Verify element {element.name} text is '{text}'") as s:
        s.error = f"expected element {element.name} text to be '{text}' but was '{element.text}'"
        s.condition = element.text == text


def verify_element_text_contains(element, text):
    """Verify element contains text

    Parameters:
    element : element
    text : value
    """
    element = browser.get_browser().find(element, timeout=0)
    with _verify_step(f"Verify element {element.name} contains text '{text}'") as s:
        s.error = f"expected element {element.name} text '{element.text}' to contain '{text}'"
        s.condition = text in element.text


def verify_element_text_is_not(element, text):
    """Verify the text of the element is not `text`

    Parameters:
    element : element
    text : value
    """
    element = browser.get_browser().find(element, timeout=0)
    with _verify_step(f"Verify element {element.name} text is not '{text}'") as s:
        s.error = f"expected element {element.name} text to not be '{text}'"
        s.condition = element.text != text


def verify_element_text_not_contains(element, text):
    """Verify the text of the element does not contain text

    Parameters:
    element : element
    text : value
    """
    element = browser.get_browser().find(element, timeout=0)
    with _verify_step(f"Verify element {element.name} does not contains text '{text}'") as s:
        s.error = f"expected element {element.name} text '{element.text}' to not contain '{text}'"
        s.condition = text not in element.text


def verify_element_value(element, value):
    """Verify element value

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element, timeout=0)
    step_message = f"Verify element {element.name} value is '{value}'"
    with _verify_step(step_message) as s:
        element_value = element.value
        s.error = f"expected element {element.name} value to be '{value}' but was '{element_value}'"
        s.condition = element_value == value


def verify_element_value_is_not(element, value):
    """Verify element value is not `value`

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element, timeout=0)
    step_message = f"Verify element {element.name} value is not '{value}'"
    with _verify_step(step_message) as s:
        element_value = element.value
        s.error = f"expected element {element.name} value to not be '{value}'"
        s.condition = element_value != value


def verify_page_contains_text(text):
    """Verify the given text is present anywhere in the page source

    Parameters:
    text : value
    """
    with _verify_step(f"Verify '{text}' is present in the page") as s:
        s.error = f"text '{text}' not found in the page"
        s.condition = text in get_browser().page_source


def verify_page_not_contains_text(text):
    """Verify the given text is not present anywhere in the page source

    Parameters:
    text : value
    """
    with _verify_step(f"Verify '{text}' is not present in the page") as s:
        s.error = f"text '{text}' was found in the page"
        s.condition = text not in get_browser().page_source


def verify_response_status_code(response, status_code):
    """Verify the response status code.

    Parameters:
    response : value
    status_code : value
    """
    with _verify_step(f'Verify response status code is {status_code}') as s:
        if isinstance(status_code, str):
            if status_code.isdigit():
                status_code = int(status_code)
        s.error = f'expected response status code to be {status_code} but ' \
                  f'was {response.status_code}'
        s.condition = response.status_code == status_code


def verify_selected_option_by_text(element, text):
    """Verify an element has a selected option by the option text

    Parameters:
    element : element
    text : value
    """
    element = get_browser().find(element)
    with _verify_step(f'Verify selected option text of element {element.name} is {text}') as s:
        selected_option_text = element.select.first_selected_option.text
        s.error = f'Expected selected option in element {element.name} to be {text} ' \
                  f'but was {selected_option_text}'
        s.condition = selected_option_text == text


def verify_selected_option_by_value(element, value):
    """Verify an element has a selected option by the option value

    Parameters:
    element : element
    value : value
    """
    element = get_browser().find(element)
    with _verify_step(f'Verify selected option value of element {element.name} is {value}') as s:
        selected_option_value = element.select.first_selected_option.value
        s.error = f'Expected selected option in element {element.name} to be {value} ' \
                  f'but was {selected_option_value}'
        s.condition = selected_option_value == value


def verify_title(title):
    """Verify the page title

    Parameters:
    title : value
    """
    with _verify_step(f"Verify page title is '{title}'") as s:
        actual_title = get_browser().title
        s.error = f"expected title to be '{title}' but was '{actual_title}'"
        s.condition = actual_title == title


def verify_title_contains(partial_title):
    """Verify the page title contains text

    Parameters:
    partial_title : value
    """
    with _verify_step(f"Verify page title contains '{partial_title}'") as s:
        s.error = f"expected title to contain '{partial_title}'"
        s.condition = partial_title in get_browser().title


def verify_title_is_not(title):
    """Verify the page title is not the given value

    Parameters:
    title : value
    """
    with _verify_step(f"Verify page title is not '{title}'") as s:
        s.error = f"expected title to not be '{title}'"
        s.condition = get_browser().title != title


def verify_title_not_contains(text):
    """Verify the page title does not contain text

    Parameters:
    text : value
    """
    with _verify_step(f"Verify page title does not contain '{text}'") as s:
        s.error = f"title contains '{text}'"
        s.condition = text not in get_browser().title


def verify_url(url):
    """Verify the current URL

    Parameters:
    url : value
    """
    current_url = get_browser().current_url
    msg = f"Verify URL is '{url}'"
    err = f"expected URL to be '{url}' but was '{current_url}'"
    with _verify_step(msg, err) as s:
        s.condition = current_url == url


def verify_url_contains(partial_url):
    """Verify the current URL contains partial_url

    Parameters:
    partial_url : value
    """
    current_url = get_browser().current_url
    msg = f"Verify URL contains '{partial_url}'"
    err = f"expected URL '{current_url}' to contain '{partial_url}'"
    with _verify_step(msg, err) as s:
        s.condition = partial_url in current_url


def verify_url_is_not(url):
    """Verify the current URL is not `url`

    Parameters:
    url : value
    """
    msg = f"Verify URL is not '{url}'"
    err = f"expected URL to not be '{url}'"
    with _verify_step(msg, err) as s:
        s.condition = get_browser().current_url != url


def verify_url_not_contains(partial_url):
    """Verify the current URL does not contain partial_url

    Parameters:
    partial_url : value
    """
    current_url = get_browser().current_url
    msg = f"Verify URL does not contain '{partial_url}'"
    err = f"expected URL '{current_url}' to not contain '{partial_url}'"
    with _verify_step(msg, err) as s:
        s.condition = partial_url not in current_url


def verify_window_present_by_partial_title(partial_title):
    """Verify there is a window/tab present by partial title

    Parameters:
    partial_title : value
    """
    with _verify_step(f"Verify window present by partial title '{partial_title}'") as s:
        s.error = f"There is no window present with partial title '{partial_title}'"
        titles = get_browser().get_window_titles()
        s.error_description = '{}\nWindow titles: {}'.format(s.error, ','.join(titles))
        s.condition = any(partial_title in t for t in titles)


def verify_window_present_by_partial_url(partial_url):
    """Verify there is a window/tab present by partial URL

    Parameters:
    partial_url : value
    """
    with _verify_step(f"Verify window present by partial URL '{partial_url}'") as s:
        s.error = f"There is no window present with partial URL '{partial_url}'"
        urls = get_browser().get_window_urls()
        s.error_description = '{}\nWindow URLs:\n{}'.format(s.error, '\n'.join(urls))
        s.condition = any(partial_url in url for url in urls)


def verify_window_present_by_title(title):
    """Verify there is a window/tab present by title

    Parameters:
    title : value
    """
    with _verify_step(f"Verify window present by title '{title}'") as s:
        s.error = f"There is no window present with title '{title}'"
        titles = get_browser().get_window_titles()
        s.error_description = '{}\nWindow titles: {}'.format(s.error, ','.join(titles))
        s.condition = title in titles


def verify_window_present_by_url(url):
    """Verify there is a window/tab present by URL

    Parameters:
    url : value
    """
    with _verify_step(f"Verify window present by URL '{url}'") as s:
        s.error = f"There is no window present with URL '{url}'"
        urls = get_browser().get_window_urls()
        s.error_description = '{}\nWindow URLs:\n{}'.format(s.error, '\n'.join(urls))
        s.condition = url in urls


def wait(seconds):
    """Wait for a fixed amount of seconds.

    Parameters:
    seconds (int or float) : value
    """
    execution.logger.info(f'Waiting for {seconds} seconds')
    try:
        to_float = float(seconds)
    except:
        raise ValueError('seconds value should be a number')
    time.sleep(to_float)


def wait_for_alert_present(timeout=30):
    """Wait for an alert to be present

    Parameters:
    timeout (optional, 30) : value
    """
    with _step('Wait for alert to be present'):
        get_browser().wait_for_alert_present(timeout)


def wait_for_element_displayed(element, timeout=30):
    """Wait for element to be present and displayed

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    with _step(f'Wait for element {element} to be displayed'):
        get_browser().wait_for_element_displayed(element, timeout)


def wait_for_element_enabled(element, timeout=30):
    """Wait for element to be enabled

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    element = get_browser().find(element, timeout=0)
    with _step(f'Wait for element {element.name} to be enabled'):
        get_browser().wait_for_element_enabled(element, timeout)


def wait_for_element_has_attribute(element, attribute, timeout=30):
    """Wait for element to have attribute

    Parameters:
    element : element
    attribute : attribute
    timeout (optional, 30) : value
    """
    element = get_browser().find(element, timeout=0)
    with _step(f'Wait for element {element.name} to have {attribute} attribute'):
        get_browser().wait_for_element_has_attribute(element, attribute, timeout)


def wait_for_element_has_not_attribute(element, attribute, timeout=30):
    """Wait for element to not have attribute

    Parameters:
    element : element
    attribute : attribute
    timeout (optional, 30) : value
    """
    element = get_browser().find(element, timeout=0)
    with _step(f'Wait for element {element.name} to not have {attribute} attribute'):
        get_browser().wait_for_element_has_not_attribute(element, attribute, timeout)


def wait_for_element_not_displayed(element, timeout=30):
    """Wait for element to be not displayed
    When element is not displayed this is ignored.
    When element is not present this will raise ElementNotFound.

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    with _step(f'Wait for element {element} to be not displayed'):
        get_browser().wait_for_element_not_displayed(element, timeout)


def wait_for_element_not_enabled(element, timeout=30):
    """Wait for element to be not enabled.

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    element = get_browser().find(element, timeout=0)
    with _step(f'Wait for element {element.name} to be not enabled'):
        get_browser().wait_for_element_not_enabled(element, timeout)


def wait_for_element_not_present(element, timeout=30):
    """Wait for element to stop being present in the DOM.
    If element is not present, this will be ignored.

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    with _step(f'Wait for element {element} to be not present'):
        get_browser().wait_for_element_not_present(element, timeout)


def wait_for_element_present(element, timeout=30):
    """Wait for element present in the DOM

    Parameters:
    element : element
    timeout (optional, 30) : value
    """
    with _step(f'Wait for element {element} to be present'):
        get_browser().wait_for_element_present(element, timeout)


def wait_for_element_text(element, text, timeout=30):
    """Wait for element text to match given text

    Parameters:
    element : element
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for element {element} text to be '{text}'"):
        get_browser().wait_for_element_text(element, text, timeout)


def wait_for_element_text_contains(element, text, timeout=30):
    """Wait for element to contain text

    Parameters:
    element : element
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for element {element} to contain text '{text}'"):
        get_browser().wait_for_element_text_contains(element, text, timeout)


def wait_for_element_text_is_not(element, text, timeout=30):
    """Wait for element text to not match given text

    Parameters:
    element : element
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for element {element} text to not be '{text}'"):
        get_browser().wait_for_element_text_is_not(element, text, timeout)


def wait_for_element_text_not_contains(element, text, timeout=30):
    """Wait for element to not contain text

    Parameters:
    element : element
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for element {element} to not contain text '{text}'"):
        get_browser().wait_for_element_text_not_contains(element, text, timeout)


def wait_for_page_contains_text(text, timeout=30):
    """Wait for page contains text in the DOM

    Parameters:
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for page contains text '{text}'"):
        get_browser().wait_for_page_contains_text(text, timeout)


def wait_for_page_not_contains_text(text, timeout=30):
    """Wait for page to not contain text in the DOM

    Parameters:
    text : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for page to not contain text '{text}'"):
        get_browser().wait_for_page_not_contains_text(text, timeout)


def wait_for_title(title, timeout=30):
    """Wait for page title to be the given title

    Parameters:
    title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for title to be '{title}'"):
        get_browser().wait_for_title(title, timeout)


def wait_for_title_contains(partial_title, timeout=30):
    """Wait for page title to contain partial_title

    Parameters:
    partial_title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for title to contain '{partial_title}'"):
        get_browser().wait_for_title_contains(partial_title, timeout)


def wait_for_title_is_not(title, timeout=30):
    """Wait for page title to not be the given title

    Parameters:
    title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for title to not be '{title}'"):
        get_browser().wait_for_title_is_not(title, timeout)


def wait_for_title_not_contains(partial_title, timeout=30):
    """Wait for page title to not contain partial_title

    Parameters:
    partial_title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for title to not contain '{partial_title}'"):
        get_browser().wait_for_title_not_contains(partial_title, timeout)


def wait_for_window_present_by_partial_title(partial_title, timeout=30):
    """Wait for window/tab present by partial title

    Parameters:
    partial_title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for window present by partial title '{partial_title}'",
               take_screenshots=False):
        get_browser().wait_for_window_present_by_partial_title(partial_title, timeout)


def wait_for_window_present_by_partial_url(partial_url, timeout=30):
    """Wait for window/tab present by partial url

    Parameters:
    partial_url : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for window present by partial url '{partial_url}'",
               take_screenshots=False):
        get_browser().wait_for_window_present_by_partial_url(partial_url, timeout)


def wait_for_window_present_by_title(title, timeout=30):
    """Wait for window/tab present by title

    Parameters:
    title : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for window present by title '{title}'", take_screenshots=False):
        get_browser().wait_for_window_present_by_title(title, timeout)


def wait_for_window_present_by_url(url, timeout=30):
    """Wait for window/tab present by url

    Parameters:
    url : value
    timeout (optional, 30) : value
    """
    with _step(f"Wait for window present by url '{url}'", take_screenshots=False):
        get_browser().wait_for_window_present_by_url(url, timeout)
