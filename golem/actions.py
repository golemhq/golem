"""Golem actions"""
import code
import importlib
import os
import pdb
import random as rand
import string
import sys
import time
import uuid

import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

import requests

from golem.core.exceptions import (TextNotPresent,
                                   ElementNotFound,
                                   TestError,
                                   TestFailure)
from golem import browser
from golem import execution


def _run_wait_hook():
    wait_hook = execution.settings['wait_hook']
    if wait_hook:
        time.sleep(0.3)
        start_time = time.time()
        extend_module = importlib.import_module('projects.{0}.extend'
                                                .format(execution.project))
        wait_hook_function = getattr(extend_module, wait_hook)
        wait_hook_function()
        execution.logger.debug('Wait hook waited for {} seconds'
                               .format(time.time() - start_time))


def _add_step(message):
    execution.steps.append(message)


def _capture_screenshot(img_id):
    """take a screenshot and store it in report_directory.
    Report_directory must already exist
    """
    driver = browser.get_browser()
    if execution.report_directory:
        img_path = os.path.join(execution.report_directory, '{}.png'.format(img_id))
        driver.get_screenshot_as_file(img_path)
    else:
        execution.logger.debug('cannot take screensot, report directory does not exist')


def _append_screenshot():
    if execution.settings['screenshot_on_step']:
        img_id = str(uuid.uuid4())[:8]
        _capture_screenshot(img_id)
        last_step = execution.steps[-1]
        execution.steps[-1] = '{}__{}'.format(last_step, img_id)


def accept_alert(ignore_not_present=False):
    """Accept an alert
    Use ignore_not_present to ignore error when alert is not present

    Parameters:
    ignore_not_present (optional, False): value"""
    step_message = 'Accept alert'
    execution.logger.info(step_message)
    _add_step(step_message)
    try:
        get_browser().switch_to.alert.accept()
    except NoAlertPresentException:
        if not ignore_not_present:
            raise
    _append_screenshot()


def activate_browser(browser_id):
    """Activates a browser by the browser_id
    
    Parameters:
    browser_id : value
    """
    step_msg = 'Activate browser {}'.format(browser_id)
    _add_step(step_msg)
    browser.activate_browser(browser_id)
    _append_screenshot()


def add_cookie(cookie_dict):
    """Add a cookie to the current session.
    
    Required keys are: "name" and "value"
    Optional keys are: "path", "domain", "secure", "expiry"
    
    Note:
    * If a cookie with the same name exists, it will be overriden.
    * This function cannot set the domain of a cookie, the domain URL
    must be visited by the browser first.
    * The domain is set automatically to the current domain the browser is in.
    * If the browser did not visit any url (initial blank page) this
    function will fail with "Message: unable to set cookie"

    Parameters:
    cookie_dict : value
    """
    execution.logger.debug('Add cookie: {}'.format(cookie_dict))
    get_browser().add_cookie(cookie_dict)


def add_error(message):
    """Add an error to the test.
    The test will continue
    Parameters:
    message : value
    """
    execution.logger.error(message)
    # execution.errors.append(message


def assert_contains(element, value):
    """DEPRECATED
    Assert element contains value
    Parameters:
    element : element
    value : value
    """
    step_message = 'Assert that {0} contains {1}'.format(element, value)
    execution.logger.info(step_message)
    execution.logger.warning('Action assert_contains is deprecated')
    _capture_or_add_step(step_message, False)
    if not value in element:
        raise Exception('Expected {} to contain {}'.format(element, value))


def assert_equals(actual_value, expected_value):
    """DEPRECATED
    Assert actual value equals expected value
    Parameters:
    actual_value : value
    expected_value : value
    """
    step_message = 'Assert that {0} equals {1}'.format(actual_value, expected_value)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not actual_value == expected_value:
        raise Exception('Expected {} to equal {}'.format(actual_value, expected_value))


def assert_false(condition):
    """DEPRECATED
    Assert condition is false
    Parameters:
    condition : value
    """
    step_message = 'Assert that {0} is false'.format(condition)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if condition:
        raise Exception('Expected {} to be false'.format(condition))


def assert_true(condition):
    """DEPRECATED
    Assert condition is true
    Parameters:
    condition : value
    """
    step_message = 'Assert that {0} is true'.format(condition)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not condition:
        raise Exception('Expected {} to be true'.format(condition))


def capture(message=''):
    """DEPRECATED, use take_screenshot instead
    Take a screenshot
    Parameters:
    message (optional) : value
    """
    execution.logger.warning('capture is DEPRECATED, Use take_screenshot instead')
    take_screenshot(message)


def clear(element):
    """DEPRECATED, use clear_element instead
    Clear an input
    Parameters:
    element : element
    """
    execution.logger.warning('clear is DEPRECATED, use clear_element instead')
    clear_element(element)


def clear_element(element):
    """Clear an input
    Parameters:
    element : element
    """
    _run_wait_hook()
    webelement = browser.get_browser().find(element)
    step_msg= 'Clear {0} element'.format(webelement.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    webelement.clear()
    _append_screenshot()


def click(element):
    """Click an element
    Parameters:
    element : element
    """
    _run_wait_hook()
    webelement = browser.get_browser().find(element)
    step_msg = 'Click {0}'.format(webelement.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    webelement.click()
    _append_screenshot()


def close():
    """DEPRECATED, use close_browser instead
    Close a browser. Closes the current active browser"""
    execution.logger.warning('close is DEPRECATED, use close_browser instead')
    close_browser()


def close_browser():
    """Close browser and all it's windows"""
    execution.logger.info('Close driver')
    get_browser().quit()
    execution.browser = None


def debug():
    """DEPRECATED, use interactive_mode instead
    Enter debug mode"""
    execution.logger.warning('debug is DEPRECATED, use interactive_mode instead')
    interactive_mode()


def delete_cookie(name):
    """Delete a cookie from the current session

    Parameters:
    name: value
    """
    execution.logger.debug('Delete cookie "{}"'.format(name))
    driver = browser.get_browser()
    cookie = driver.get_cookie(name)
    if not cookie:
        raise Exception('Cookie "{}" was not found'.format(name))
    else:
        driver.delete_cookie(name)


def delete_all_cookies():
    """Delete all cookies from the current session.

    Note: this only deletes cookies from the current domain.
    """
    execution.logger.debug('Delete all cookies')
    get_browser().delete_all_cookies()


def dismiss_alert(ignore_not_present=False):
    """Dismiss an alert.
    Use ignore_not_present=True to ignore error when alert is not present

    Parameters:
    ignore_not_present (optional, False) : value"""
    step_message = 'Dismiss alert'
    execution.logger.info(step_message)
    _add_step(step_message)
    try:
        get_browser().switch_to.alert.dismiss()
    except NoAlertPresentException:
        if not ignore_not_present:
            raise
    _append_screenshot()


def double_click(element):
    """Double click an element
    Parameters:
    element : element
    """
    element = browser.get_browser().find(element)
    step_message = 'Double click element {}'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.double_click()
    _append_screenshot()


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
#     _append_screenshot()


def execute_javascript(script, *args):
    """Execute javascript code

    Parameters:
    script : value
    *args : value
    """
    return get_browser().execute_script(script, *args)


def error(message=''):
    """Mark the test as error and stop.

    Parameters:
    message (optional): value
    """
    add_error(message)
    raise TestError(message)


def fail(message=''):
    """Mark the test as failure and stop

    Parameters:
    message (optional) : value"""
    # TODO
    raise TestFailure(message)


def focus_element(element):
    """Give focus to element
    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = 'Focus element {}'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.focus()
    _append_screenshot()


def get(url):
    """Navigate to the given URL
    Parameters:
    url : value
    """
    navigate(url)


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
    execution.logger.debug('Get cookie "{}"'.format(name))
    return get_browser().get_cookie(name)


def get_cookies():
    """Returns a list of dictionaries, corresponding to cookies
    visible in the current session.
    """
    execution.logger.debug('Get all cookies')
    return get_browser().get_cookies()


def get_current_url():
    """Return the current browser URL"""
    return get_browser().current_url


def get_search_timeout():
    """Get search timeout"""
    return execution.settings['search_timeout']


def go_back():
    """Goes one step backward in the browser history"""
    _run_wait_hook()
    step_msg = 'Go back'
    execution.logger.debug(step_msg)
    _add_step(step_msg)
    browser.get_browser().back()
    _append_screenshot()


def interactive_mode():
    """Enter interactive mode"""
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
    _run_wait_hook()
    element = browser.get_browser().find(element)
    step_msg = 'Javascript click element {0}'.format(element.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    element.javascript_click()
    _append_screenshot()


def mouse_hover(element):
    """DEPRECATED, used mouse_over instead
    Hover an element with the mouse

    Parameters:
    element : element
    """
    execution.logger.warning('mouse_over is DEPRECATED, use mouse_over instead')


def mouse_over(element):
    """Perform a mouse over on element

    Parameters:
    element : element
    """
    _run_wait_hook()
    driver = browser.get_browser()
    element = driver.find(element)
    step_message = 'Mouse over element \'{0}\''.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.mouse_over()
    _append_screenshot()


def navigate(url):
    """Navigate to a URL

    Parameters:
    url : value
    """
    step_msg = 'Navigate to: \'{0}\''.format(url)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    browser.get_browser().get(url)
    _append_screenshot()
    

def open_browser(browser_id=None):
    """Open a new browser.
    browser_id is optional and only used to manage more than one
    browser at the same time.

    Parameters:
    browser_id (optional) : value
    """
    step_message = 'Open browser'
    execution.logger.info(step_message)
    _add_step(step_message)
    browser.open_browser(browser_id)

    
def press_key(element, key):
    """Press a given key in the element.

    Parameters:
    element : element
    key : value
    """
    element = get_browser().find(element)
    step_message = 'Press key: {} in element {}'.format(key, element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.press_key(key)
    _append_screenshot()


def random(value):
    """Generate a random string value.
    TODO
    Parameters:
    value : value
    """
    random_string = ''
    for char in value:
        if char == 'c':
            random_string += rand.choice(string.ascii_lowercase)
        elif char == 'd':
            random_string += str(rand.randint(0, 9))
        else:
            random_string += char
    execution.logger.info('Random value generated: {}'.format(random_string))
    return random_string


def refresh_page():
    """Refresh the page."""
    _run_wait_hook()
    step_message = 'Refresh page'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().refresh()
    _append_screenshot()


def select_by_index(element, index):
    """DEPRECATED, use select_option_by_index
    Select an option from a select dropdown by index.

    Parameters:
    element : element
    index : value
    """
    execution.logger.warning('select_by_index is DEPRECATED, use select_option_by_index instead')
    select_option_by_index(element, index)


def select_by_text(element, text):
    """DEPRECATED, use select_option_by_text
    Select an option from a select dropdown by text.

    Parameters:
    element : element
    text : value
    """
    execution.logger.warning('select_by_text is DEPRECATED, use select_option_by_text instead')
    select_option_by_text(element, text)


def select_by_value(element, value):
    """DEPRECATED, use select_option_by_value

    Parameters:
    element : element
    value : value
    """
    execution.logger.warning('select_by_value is DEPRECATED, use select_option_by_value instead')
    select_option_by_value(element, value)


def select_option_by_index(element, index):
    """Select an option from a select dropdown by index.

    Parameters:
    element : element
    index : value
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = 'Select option of index {0} from element {1}'.format(index, element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.select.select_by_index(index)
    _append_screenshot()


def select_option_by_text(element, text):
    """Select an option from a select dropdown by text.

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = 'Select \'{0}\' from element {1}'.format(text, element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.select.select_by_visible_text(text)
    _append_screenshot()


def select_option_by_value(element, value):
    """Select an option from a select dropdown by value.

    Parameters:
    element : element
    value : value
    """
    _run_wait_hook()
    element = browser.get_browser().find(element)
    step_message = 'Select \'{0}\' value from element {1}'.format(value, element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.select.select_by_value(value)
    _append_screenshot()


def send_keys(element, text):
    """Send keys to element.

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = 'Write \'{0}\' in element {1}'.format(text, element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.send_keys(text)
    _append_screenshot()


def send_text_to_alert(text):
    """Send text to an alert

    Parameters:
    text : value
    """
    _run_wait_hook()
    step_message = 'Send \'{}\' to alert'.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to.alert.send_keys(text)
    _append_screenshot()


def set_browser_capability(capability_key, capability_value):
    """Set a browser capability.
    Call this action before starting the browser for the
    capability to take effect.

    Parameters:
    capability_key : value
    capability_value : value
    """
    step_message = ('Set browser cabability "{}" to "{}"'
                    .format(capability_key, capability_value))
    execution.logger.debug(step_message)
    execution.browser_definition['capabilities'][capability_key] = capability_value


def set_search_timeout(timeout):
    """Set the search timeout value
    Parameters:
    timeout : value
    """
    execution.logger.debug('Set search_timeout to: {}'.format(timeout))
    if not isinstance(timeout, int) and not isinstance(timeout, float):
        raise ValueError('timeout must be int or float')
    else:
        execution.settings['search_timeout'] = timeout


def set_trace():
    """Set trace for Python pdb
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
    _run_wait_hook()
    step_message = 'Set browser window size to {0}x, {1}y.'.format(width, height)
    execution.logger.debug(step_message)
    get_browser().set_window_size(width, height)


def step(message):
    """Log a step to the report.

    Parameters:
    message : value
    """
    execution.logger.info(message)
    execution.steps.append(message)


def store(key, value):
    """Store a value in data

    Parameters:
    key : value
    value : value
    """
    execution.logger.info('Store value {} in key {}'.format(value, key))
    setattr(execution.data, key, value)


def submit_prompt_alert(text):
    """Send text to alert and accept it

    Parameters:
    text : value
    """
    _run_wait_hook()
    step_message = 'Submit alert with text \'{}\''.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to.alert.send_keys(text)
    get_browser().switch_to.alert.accept()
    _append_screenshot()


def take_screenshot(message=''):
    """Take a screenshot
    Parameters:
    message (optional) : value
    """
    _run_wait_hook()
    step_msg = 'Take screenshot'
    if message:
        step_msg += ': {}'.format(message)
    execution.logger.info(step_msg)
    img_id = str(uuid.uuid4())[:8]
    step_msg = '{}__{}'.format(step_msg, img_id)
    _add_step(step_msg)
    _capture_screenshot(img_id)


def verify_alert_is_present():
    """DEPRECATED, use verify_alert_present"""
    execution.logger.warning('verify_alert_is_present is DEPRECATED, use verify_alert_present instead')
    verify_alert_present()


def verify_alert_is_not_present():
    """DEPRECATED, use verify_alert_not_present.
    Verify an alert is not present"""
    execution.logger.warning('verify_alert_is_not_present is DEPRECATED, use verify_alert_not_present instead')
    verify_alert_not_present()


def verify_alert_present():
    """Verify an alert is present"""
    step_message = 'Verify an alert is present'
    execution.logger.info(step_message)
    _add_step(step_message)
    assert get_browser().alert_is_present(), 'an alert was not present'
    _append_screenshot()


def verify_alert_not_present():
    """Verify an alert is not present"""
    step_message = 'Verify an alert is not present'
    execution.logger.info(step_message)
    _add_step(step_message)
    assert not get_browser().alert_is_present(), 'an alert was present'
    _append_screenshot()


def verify_alert_text(text):
    """Verify alert text

    Parameters:
    text : value
    """
    step_message = 'Verify alert text is \'{}\''.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    alert_text = get_browser().switch_to.alert.text
    error_msg = 'Expected alert text to be \'{}\' but was \'{}\''.format(text, alert_text)
    assert alert_text == text, error_msg
    _append_screenshot()


def verify_alert_text_is_not(text):
    """Verify alert text is not text

    Parameters:
    text : value
    """
    step_message = 'Verify alert text is not \'{}\''.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    alert_text = get_browser().switch_to.alert.text
    error_msg = 'Expected alert text not to be \'{}\''.format(text)
    assert alert_text != text, error_msg
    _append_screenshot()


def verify_cookie_value(name, value):
    """Verify the value of a cookie.

    Parameters:
    name: value
    value: value
    """
    _run_wait_hook()
    step_message = 'Verify that cookie "{}" value is "{}"'.format(name, value)
    execution.logger.info(step_message)
    _add_step()
    cookie = browser.get_browser().get_cookie(name)
    if not cookie:
        raise Exception('Cookie "{}" was not found'.format(name))
    elif not 'value' in cookie:
        raise Exception('Cookie "{}" did not have "value" key'.format(name))
    elif cookie['value'] != value:
        msg = ('Expected cookie "{}" value to be "{}" but was "{}"'
               .format(name, value, cookie['value']))
        raise Exception(msg)
         

def verify_cookie_exists(name):
    """DEPRECATED, use verify_cookie_present
    Verify a cookie exists in the current session.
    The cookie is found by its name.

    Parameters:
    name: value
    """
    execution.logger.warning('verify_cookie_exists is DEPRECATED, use verify_cookie_present')


def verify_cookie_present(name):
    """Verify a cookie exists in the current session.
    The cookie is found by its name.

    Parameters:
    name: value
    """
    step_message = 'Verify that cookie "{}" exists'.format(name)
    execution.logger.info(step_message)
    _add_step(step_message)
    cookie = browser.get_browser().get_cookie(name)
    if not cookie:
        raise Exception('Cookie "{}" was not found'.format(name))


def verify_element_checked(element):
    """Verify element is checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} is checked'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    assert element.is_selected(), 'element {} is not checked'.format(element.name)
    _append_screenshot()


def verify_element_displayed(element):
    """Verify element is displayed

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    step_message = 'Verify element {} is displayed'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    if not element.is_displayed():
        raise Exception('element {} is not displayed'.format(element.name))
    _append_screenshot()


def verify_element_enabled(element):
    """Verify element is enabled.

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} is enabled'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    if not element.is_enabled():
        raise Exception('Element is not enabled')
    _append_screenshot()


def verify_element_has_attribute(element, attribute):
    """Verify element has attribute

    Parameters:
    element : element
    attribute : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify element {} has attribute {}'.format(element.name, attribute)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = 'element {} does not have attribute {}'.format(element.name, attribute)
    assert element.has_attribute(attribute), error_msg
    _append_screenshot()


def verify_element_has_focus(element):
    """Verify element has focus

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify element {} has focus'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = 'element {} does not have focus'.format(element.name)
    assert element.has_focus(), error_msg


def verify_element_has_not_attribute(element, attribute):
    """Verify element has not attribute

    Parameters:
    element : element
    attribute : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify element {} has not attribute {}'.format(element.name, attribute)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = 'element {} has attribute {}'.format(element.name, attribute)
    assert not element.has_attribute(attribute), error_msg


def verify_element_has_not_focus(element):
    """Verify element does not have focus

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify element {} does not have focus'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = 'element {} has focus'.format(element.name)
    assert not element.has_focus(), error_msg


def verify_element_not_checked(element):
    """Verify element is not checked.
    This applies to checkboxes and radio buttons.

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = browser.get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} is not checked'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    assert not element.is_selected(), 'element {} is checked'.format(element.name)
    _append_screenshot()


def verify_element_not_displayed(element):
    """Verify element is not displayed

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0, wait_displayed=False)
    step_message = 'Verify element {} is not displayed'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    if element.is_displayed():
        raise Exception('element {} is displayed'.format(element.name))
    _append_screenshot()


def verify_element_not_enabled(element):
    """Verify element is not enabled.

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} is not enabled'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    if element.is_enabled():
        raise Exception('Element is enabled')
    _append_screenshot()


def verify_element_not_present(element):
    """Verify element is not present in the DOM

    Parameters:
    element : element
    """
    _run_wait_hook()
    step_message = 'Verify element is not present'
    execution.logger.info(step_message)
    _add_step(step_message)
    try:
        element = get_browser().find(element, timeout=0)
        raise Exception('element {} is present'.format(element.name))
    except:
        pass


def verify_element_present(element):
    """Verify element is present in the DOM

    Parameters:
    element : element
    """
    _run_wait_hook()
    step_message = 'Verify element is present'
    execution.logger.info(step_message)
    _add_step(step_message)
    try:
        get_browser().find(element, timeout=0)
    except ElementNotFound:
        raise ElementNotFound('element is not present')


def verify_element_text(element, text):
    """Verify the text of the element

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = browser.get_browser().find(element, timeout=0)
    step_message = 'Verify element {0} text is \'{1}\''.format(element.name, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if element.text != text:
        raise Exception(("expected element {} text to be '{}' but was '{}'"
                         .format(element.name, text, element.text)))
    _append_screenshot()


def verify_element_text_contains(element, text):
    """Verify element contains text

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = browser.get_browser().find(element, timeout=0)
    step_message = 'Verify element {0} contains text \'{1}\''.format(element.name, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if text not in element.text:
        raise Exception(("expected element {} to contain text '{}'"
                         .format(element.name, text)))
    _append_screenshot()


def verify_element_text_is_not(element, text):
    """Verify the text of the element is not text

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = browser.get_browser().find(element, timeout=0)
    step_message = 'Verify element {0} text is not \'{1}\''.format(element.name, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if element.text == text:
        raise Exception(("expected element {} text to not be '{}'"
                         .format(element.name, text)))
    _append_screenshot()


def verify_element_text_not_contains(element, text):
    """Verify the text of the element does not contain text

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = browser.get_browser().find(element, timeout=0)
    step_message = 'Verify element {0} does not contain text \'{1}\''.format(element.name, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if text in element.text:
        raise Exception("element {} contains text '{}'".format(element.name, text))
    _append_screenshot()


def verify_exists(element):
    """Verify that en element exists.
    Parameters:
    element : element
    """
    _run_wait_hook()
    step_message = 'Verify that the element exists'
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    try:
        webelement = browser.get_browser().find(element, timeout=1)
    except:
        raise ElementNotFound('Element {} does not exist'.format(element))


def verify_is_enabled(element):
    """DEPRECATED, use verify_element_enabled
    Verify an element is enabled.

    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_enabled is DEPRECATED, use verify_element_enabled')
    verify_element_enabled(element)


def verify_is_not_enabled(element):
    """DEPRECATED, use verify_element_not_enabled
    Verify an element is not enabled

    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_not_enabled is DEPRECATED, use verify_element_not_enabled')
    verify_element_not_enabled(element)


def verify_is_not_selected(element):
    """DEPRECATED, use verify_element_not_checked

    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_not_selected is DEPRECATED, use verify_element_not_checked')
    verify_element_not_checked(element)


def verify_is_not_visible(element):
    """DEPRECATED, use verify_element_not_displayed

    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_not_visible is DEPRECATED, use verify_element_not_displayed')
    verify_element_not_displayed(element)


def verify_is_selected(element):
    """DEPRECATED, use verify_element_checked

    Verify an element is selected
    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_selected is DEPRECATED, use verify_element_checked')
    verify_element_checked(element)


def verify_is_visible(element):
    """DEPRECATED, use verify_element_displayed

    Parameters:
    element : element
    """
    execution.logger.warning('verify_is_visible is DEPRECATED, use verify_element_displayed')
    verify_element_displayed(element)


def verify_not_exists(element):
    """DEPRECATED, use verify_element_not_present

    Parameters:
    element : element
    """
    execution.logger.warning('verify_not_exists is DEPRECATED, use verify_element_not_present')
    verify_element_not_present(element)


def verify_page_contains_text(text):
    """Verify the given text is present anywhere in the page code

    Parameters:
    text : value
    """
    _run_wait_hook()
    step_message = 'Verify \'{0}\' is present in page'.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if text not in get_browser().page_source:
        raise TextNotPresent("Text '{}' not found in page".format(text))
    _append_screenshot()


def verify_page_not_contains_text(text):
    """Verify the given text is not present anywhere in the page code

    Parameters:
    text : value
    """
    _run_wait_hook()
    step_message = 'Verify \'{0}\' is not present in page'.format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    if text in get_browser().page_source:
        raise Exception("text '{}' was found in page".format(text))
    _append_screenshot()


def verify_selected_option(element, text):
    """DEPRECATED, use verify_selected_option_by_text or verify_selected_option_by_value

    Verify an element has a selected option, passed by option text.
    Parameters:
    element : element
    text : value
    """
    execution.logger.warning(('verify_selected_option is DEPRECATED, use '
                              'verify_selected_option_by_text or '
                              'verify_selected_option_by_value'))
    verify_selected_option_by_text(element, text)


def verify_selected_option_by_text(element, text):
    """Verify an element has a selected option by the option text

    Parameters:
    element : element
    text : value
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = ('Verify selected option text of element {} is {}'
                    .format(element.name, text))
    execution.logger.info(step_message)
    _add_step(step_message)
    selected_option_text = element.select.first_selected_option.text
    error_msg = ('Expected selected option in element {} to be {} but was {}'
                 .format(element.name, text, selected_option_text))
    assert selected_option_text == text, error_msg
    _append_screenshot()


def verify_selected_option_by_value(element, value):
    """Verify an element has a selected option by the option value

    Parameters:
    element : element
    value : value
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = ('Verify selected option value of element {} is {}'
                    .format(element.name, value))
    execution.logger.info(step_message)
    _add_step(step_message)
    selected_option_value = element.select.first_selected_option.value
    error_msg = ('Expected selected option in element {} to be {} but was {}'
                 .format(element.name, value, selected_option_value))
    assert selected_option_value == value, error_msg
    _append_screenshot()


def verify_text(text):
    """DEPRECATED, use verify_page_contains_text

    Parameters:
    text : value
    """
    execution.logger.warning('verify_text is DEPRECATED, use verify_page_contains_text')
    verify_page_contains_text(text)


def verify_text_in_element(element, text):
    """DEPRECATED, use verify_element_text

    Parameters:
    element : element
    text : value
    """
    execution.logger.warning('verify_text_in_element is DEPRECATED, use verify_element_text or verify_element_text_contains')
    verify_element_text_contains(element, text)


def verify_title(title):
    """Verify the page title

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = "Verify page title is '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = ("expected title to be '{}' but was '{}'"
                 .format(title, get_browser().title))
    assert get_browser().title == title, error_msg
    _append_screenshot()


def verify_title_contains(text):
    """Verify the page title contains text

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = "Verify page title contains '{}'".format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "expected title to contain '{}'".format(text)
    assert text in get_browser().title, error_msg
    _append_screenshot()


def verify_title_is_not(title):
    """Verify the page title is not title

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = "Verify page title is not '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "expected title to not be '{}'".format(title)
    assert get_browser().title != title, error_msg
    _append_screenshot()


def verify_title_not_contains(text):
    """Verify the page title does not contain text

    Parameters:
    text : value
    """
    _run_wait_hook()
    step_message = "Verify page title does not contain '{}'".format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "title contains '{}'".format(text)
    assert text not in get_browser().title, error_msg
    _append_screenshot()


def verify_url(url):
    """Verify the current URL

    Parameters:
    url : value
    """
    _run_wait_hook()
    step_message = "Verify URL is '{}'".format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = ("expected URL to be '{}' but was '{}'"
                 .format(url, get_browser().current_url))
    assert get_browser().current_url == url, error_msg
    _append_screenshot()


def verify_url_contains(partial_url):
    """Verify the current URL contains partial_url

    Parameters:
    partial_url : value
    """
    _run_wait_hook()
    step_message = "Verify URL contains '{}'".format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "expected URL to contain '{}'".format(partial_url)
    assert partial_url in get_browser().current_url, error_msg
    _append_screenshot()


def verify_url_is_not(url):
    """Verify the current URL is not url

    Parameters:
    url : value
    """
    _run_wait_hook()
    step_message = "Verify URL is not '{}'".format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "expected URL to not be '{}'".format(url)
    assert get_browser().current_url != url, error_msg
    _append_screenshot()


def verify_url_not_contains(partial_url):
    """Verify the current URL does not contain partial_url

    Parameters:
    partial_url : value
    """
    _run_wait_hook()
    step_message = "Verify page title does not contain '{}'".format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "URL contains '{}'".format(partial_url)
    assert partial_url not in get_browser().current_urlverify_url_not_contains, error_msg
    _append_screenshot()


def wait(seconds):
    """Wait for a fixed amount of seconds.
    Parameters:
    seconds (int or float) : value
    """
    execution.logger.info('Waiting for {} seconds'.format(seconds))
    try:
        to_float = float(seconds)
    except:
        raise Exception('seconds value should be a number')
    time.sleep(to_float)


def wait_for_alert_present(timeout=30):
    """Wait for an alert to be present

    Parameters:
    timeout (30) : value
    """
    step_message = 'Wait for alert to be present'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_alert_present(timeout)
    _append_screenshot()


def wait_for_element_enabled(element, timeout=20):
    """Wait for element to be enabled.

    Parameters:
    element : element
    timeout (20) : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Waiting for element {} to be enabled'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_enabled(element, timeout)
    _append_screenshot()


def wait_for_element_not_present(element, timeout=30):
    """Wait for element to stop being present in the DOM.

    Parameters:
    element : element
    timeout (20) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to be not present'.format(element)
    execution.logger.info(step_message)
    _add_step(step_message)
    try:
        element = get_browser().find(element, timeout=0, wait_displayed=False)
        get_browser().wait_for_element_not_present(element, timeout)
    except ElementNotFound:
        execution.logger.debug('element {} is not present'.format(element))
    _append_screenshot()


def wait_for_element_not_exist(element, timeout=20):
    """Wait for a webelement to stop existing in the DOM.
    If the webelement still exists after the timeout
    ended, it will not raise an exception.
    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    execution.logger.warning('wait_for_element_not_exists is DEPRECATED, use wait_for_element_not_present')
    wait_for_element_not_present()


def wait_for_element_not_visible(element, timeout=20):
    """Wait for an element to stop being visible.
    After the timeout, this won't throw an exception.
    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    execution.logger.info('Waiting for element {} to be not visible'.format(element))
    webelement = None
    try:
        webelement = browser.get_browser().find(element, timeout=3)
    except:
        execution.logger.debug('Element is already not visible, continuing...')
        return
    if webelement:
        start_time = time.time()
        timed_out = False
        while webelement.is_displayed() and not timed_out:
            execution.logger.debug('Element is still visible, waiting...')
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                timed_out = True
                execution.logger.info('Timeout, element is still visible.')


def wait_for_element_present(element, timeout=30):
    """Wait for element present in the DOM

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to be present'.format(element)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_present(element, timeout)
    _append_screenshot()


def wait_for_element_visible(element, timeout=20):
    """Wait for element to be visible.
    After timeout this won't throw an exception.
    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    _run_wait_hook()
    execution.logger.info('Waiting for element {} to be visible'.format(element))
    start_time = time.time()
    timed_out = False
    webelement = browser.get_browser().find(element)
    while not webelement.is_displayed() and not timed_out:
        execution.logger.debug('Element is not visible, waiting..')
        time.sleep(0.5)
        if time.time() - start_time > timeout:
            timed_out = True


def http_get(url, headers={}, params={}, verify_ssl_cert=True):
    """Perform an HTTP GET request to the given URL.
    Headers and params are optional dictionaries.
    
    Parameters:
    url : value
    headers (optional, dict) : value
    params (optional, dict) : value
    verify_ssl_cert (optional, default is True) : value
    """
    step_message = 'Make GET request to {}'.format(url)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.get(url, headers=headers, params=params, verify=verify_ssl_cert)
    store('last_response', response)


def http_post(url, headers={}, data={}, verify_ssl_cert=True):
    """Perform an HTTP POST request to the given URL.
    Headers and data are optional dictionaries.
    
    Parameters:
    url : value
    headers (optional, dict) : value
    data (optional, dict) : value
    verify_ssl_cert (optional, default is True) : value
    """
    step_message = 'Make POST request to {}'.format(url)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.post(url, headers=headers, data=data, verify=verify_ssl_cert)
    store('last_response', response)


def verify_response_status_code(response, status_code):
    """Verify the response status code.
    Parameters:
    response : value
    status_code : value
    """
    if isinstance(status_code, str):
        if status_code.isdigit():
            status_code = int(status_code)
    step_message = 'Verify response status code is {}'.format(status_code)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not response.status_code == status_code:
        raise Exception("Expected response status code to be {0} but was {1}"
                        .format(status_code, response.status_code))


# def verify_response_content():
#     pass
