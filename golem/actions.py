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

import requests

from golem import browser
from golem import execution
from golem.core.exceptions import (TextNotPresent,
                                   TestError,
                                   TestFailure)


def _add_error(short_error, long_error, log_level='ERROR'):
    execution.errors.append()

def _add_step(message):
    execution.steps.append(message)

def _append_screenshot():
    if execution.settings['screenshot_on_step']:
        img_id = str(uuid.uuid4())[:8]
        _capture_screenshot(img_id)
        last_step = execution.steps[-1]
        execution.steps[-1] = '{}__{}'.format(last_step, img_id)


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


def accept_alert(ignore_not_present=False):
    """Accept an alert
    When ignore_not_present is True the error when alert
    is not present is ignored.

    Parameters:
    ignore_not_present (False): value"""
    step_message = 'Accept alert'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().accept_alert(ignore_not_present)
    _append_screenshot()


def activate_browser(browser_id):
    """Activates a browser by the browser_id
    
    Parameters:
    browser_id : value
    """
    step_message = 'Activate browser {}'.format(browser_id)
    execution.logger.info(step_message)
    _add_step(step_message)
    browser.activate_browser(browser_id)
    _append_screenshot()


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
    execution.logger.debug('Add cookie: {}'.format(cookie_dict))
    get_browser().add_cookie(cookie_dict)


def add_error(message):
    """Add an error to the test.
    The test will continue
    Parameters:
    message : value
    """
    execution.logger.error(message)


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
    _add_step(step_message)
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
    _add_step(step_message)
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
    _add_step(step_message)
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
    _add_step(step_message)
    if not condition:
        raise Exception('Expected {} to be true'.format(condition))


def capture(message=''):
    """DEPRECATED, use take_screenshot
    Take a screenshot
    Parameters:
    message (optional) : value
    """
    execution.logger.warning('capture is DEPRECATED, Use take_screenshot')
    take_screenshot(message)


def check_element(element):
    """Check an element (checkbox or radiobutton).
    If element is already checked this is is ignored.

    Parameters:
    element : element
    """
    element = get_browser().find(element)
    step_msg = 'Check element {}'.format(element.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    get_browser().check_element(element)
    _append_screenshot()


def clear(element):
    """DEPRECATED, use clear_element
    Clear an input
    Parameters:
    element : element
    """
    execution.logger.warning('clear is DEPRECATED, use clear_element')
    clear_element(element)


def clear_element(element):
    """Clear an element (e.g. a text input)

    Parameters:
    element : element
    """
    _run_wait_hook()
    element = get_browser().find(element)
    step_message = 'Clear element {}'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.clear()
    _append_screenshot()


def click(element):
    """Click element

    Parameters:
    element : element
    """
    _run_wait_hook()
    webelement = browser.get_browser().find(element)
    step_message = 'Click {}'.format(webelement.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    webelement.click()
    _append_screenshot()


def close():
    """DEPRECATED, use close_browser or close_window
    Close a browser. Closes the current active browser"""
    execution.logger.warning('close is DEPRECATED, use close_browser or close_window')
    close_browser()


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
    execution.logger.info('Close current window')
    browser = get_browser()
    browser.close()
    if browser.window_handles:
        browser.switch_to_first_window()


def close_window_by_index(index):
    """Close window/tab by index.
    Note: "The order in which the window handles are returned is arbitrary."

    Parameters:
    index : value
    """
    _run_wait_hook()
    step_message = 'Close window by index {}'.format(index)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().close_window_by_index(index)
    _append_screenshot()


def close_window_by_partial_title(partial_title):
    """Close window/tab by partial title

    Parameters:
    partial_title : value
    """
    _run_wait_hook()
    step_message = 'Close window by partial title \'{}\''.format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().close_window_by_partial_title(partial_title)
    _append_screenshot()


def close_window_by_partial_url(partial_url):
    """Close window/tab by partial URL

    Parameters:
    partial_title : value
    """
    _run_wait_hook()
    step_message = 'Close window by partial URL \'{}\''.format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().close_window_by_partial_url(partial_url)
    _append_screenshot()


def close_window_by_title(title):
    """Close window/tab by title

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = 'Close window by title \'{}\''.format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().close_window_by_title(title)
    _append_screenshot()


def close_window_by_url(url):
    """Close window/tab by URL

    Parameters:
    url : value
    """
    _run_wait_hook()
    step_message = 'Close window by URL \'{}\''.format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().close_window_by_url(url)
    _append_screenshot()


def debug():
    """DEPRECATED, use interactive_mode
    Enter debug mode"""
    execution.logger.warning('debug is DEPRECATED, use interactive_mode')
    interactive_mode()


def delete_all_cookies():
    """Delete all cookies from the current session.
    Note: this only deletes cookies from the current domain.
    """
    execution.logger.debug('Delete all cookies')
    get_browser().delete_all_cookies()


def delete_cookie(name):
    """Delete a cookie from the current session

    Parameters:
    name: value
    """
    execution.logger.debug('Delete cookie "{}"'.format(name))
    browser = get_browser()
    cookie = browser.get_cookie(name)
    if not cookie:
        raise Exception('Cookie "{}" was not found'.format(name))
    else:
        browser.delete_cookie(name)


def dismiss_alert(ignore_not_present=False):
    """Dismiss an alert.
    When ignore_not_present is True the error when alert
    is not present is ignored.

    Parameters:
    ignore_not_present (False) : value"""
    step_message = 'Dismiss alert'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().dismiss_alert(ignore_not_present)
    _append_screenshot()


def double_click(element):
    """Double click an element

    Parameters:
    element : element
    """
    element = get_browser().find(element)
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


def error(message=''):
    """Mark the test as error and stop.

    Parameters:
    message (optional): value
    """
    add_error(message)
    raise TestError(message)


def execute_javascript(script, *args):
    """Execute javascript code

    Parameters:
    script : value
    *args : value
    """
    execution.logger.debug('Execute javascript code \'{}\' with args \'{}\''.format(script, args))
    return get_browser().execute_script(script, *args)


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
    execution.logger.debug('Get cookie "{}"'.format(name))
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


def get_element_attribute(element, attribute):
    """Get the attribute value of element.
    If the attribute is not present in element, None is returned.

    Parameters
    element : element
    attribute : value
    """
    return get_browser().find(element).get_attribute(attribute)


def get_element_text(element):
    """Get the element text

    Parameters
    element : element
    """
    return get_browser().find(element).text


def get_element_value(element):
    """Get the element value attribute

    Parameters
    element : element
    """
    return get_browser().find(element).get_attribute('value')


def get_page_source():
    """Get the page source"""
    return get_browser().page_source


def get_search_timeout():
    """Get search timeout"""
    return execution.settings['search_timeout']


def get_window_handle():
    """Get window handle"""
    return get_browser().current_window_handle


def get_window_handles():
    """Return a list with the handles of all the open windows/tabs"""
    return get_browser().window_handles


def get_window_index():
    """"Get the index of the current window/tab"""
    return get_browser().get_window_index()


def get_window_title():
    """Get window title"""
    return get_browser().title


def get_window_titles():
    """Return a list with the titles of all the open windows/tabs"""
    execution.logger.debug('Get window titles')
    return get_browser().get_window_titles()


def go_back():
    """Goes one step backward in the browser history"""
    _run_wait_hook()
    step_message = 'Go back'
    execution.logger.info(step_message)
    _add_step(step_message)
    browser.get_browser().back()
    _append_screenshot()


def go_forward():
    """Goes one step forward in the browser history"""
    _run_wait_hook()
    step_msg = 'Go forward'
    execution.logger.info(step_msg)
    _add_step(step_msg)
    browser.get_browser().forward()
    _append_screenshot()


def http_get(url, headers={}, params={}, verify_ssl_cert=True):
    """Perform an HTTP GET request to the given URL.
    Headers and params are optional dictionaries.

    Parameters:
    url : value
    headers (optional, dict) : value
    params (optional, dict) : value
    verify_ssl_cert (optional, True) : value
    """
    step_message = 'Make a GET request to {}'.format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    response = requests.get(url, headers=headers, params=params,
                            verify=verify_ssl_cert)
    store('last_response', response)
    return response


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
    _add_step(step_message)
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
    _run_wait_hook()
    element = get_browser().find(element)
    step_msg = 'Javascript click element {}'.format(element.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    element.javascript_click()
    _append_screenshot()


def maximize_window():
    """Maximize browser window"""
    execution.logger.debug('maximize browser window')
    get_browser().maximize_window()
    _append_screenshot()


def mouse_hover(element):
    """DEPRECATED, used mouse_over
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
    step_message = 'Mouse over element \'{}\''.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    element.mouse_over()
    _append_screenshot()


def navigate(url):
    """Navigate to a URL

    Parameters:
    url : value
    """
    step_message = 'Navigate to: \'{0}\''.format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
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
    """Press a given key in element.

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
    """Refresh the page"""
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
    execution.logger.warning('select_by_index is DEPRECATED, use select_option_by_index')
    select_option_by_index(element, index)


def select_by_text(element, text):
    """DEPRECATED, use select_option_by_text
    Select an option from a select dropdown by text.

    Parameters:
    element : element
    text : value
    """
    execution.logger.warning('select_by_text is DEPRECATED, use select_option_by_text')
    select_option_by_text(element, text)


def select_by_value(element, value):
    """DEPRECATED, use select_option_by_value

    Parameters:
    element : element
    value : value
    """
    execution.logger.warning('select_by_value is DEPRECATED, use select_option_by_value')
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
    element = get_browser().find(element)
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
    step_message = ('Set browser capability "{}" to "{}"'
                    .format(capability_key, capability_value))
    execution.logger.debug(step_message)
    execution.browser_definition['capabilities'][capability_key] = capability_value


def set_search_timeout(timeout):
    """Set the search timeout value

    Paramters:
    timeout : value
    """
    execution.logger.debug('Set search_timeout to: {}'.format(timeout))
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


def submit_form(element):
    """Submit form.
    Element can be the form itself or any child element.

    Parameters:
    element: element
    """
    element = get_browser().find(element)
    step_msg = 'Submit form'
    execution.logger.info(step_msg)
    _add_step(step_msg)
    get_browser().find(element).submit()
    _append_screenshot()


def submit_prompt_alert(text):
    """Send text to a prompt alert and accept it

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


def switch_to_default_content():
    """Switch to default content (default frame)"""
    _run_wait_hook()
    step_message = 'Switch to default content'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to.default_content()
    _append_screenshot()


def switch_to_first_window():
    """Switch to first window/tab"""
    _run_wait_hook()
    step_message = 'Switch to first window'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_first_window()
    _append_screenshot()


def switch_to_frame(frame):
    """Switch to frame.
    frame must be the index, name, or the frame webelement itself.

    Parameters:
    frame : value
    """
    _run_wait_hook()
    step_message = 'Switch to frame {}'.format(frame)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to.frame(frame)
    _append_screenshot()


def switch_to_last_window():
    """Switch to last window/tab"""
    _run_wait_hook()
    step_message = 'Switch to last window'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_last_window()
    _append_screenshot()


def switch_to_next_window():
    """Switch to next window/tab in the list of window handles.
    If current window is the last in the list of window handles this
    will circle back from the start.
    """
    _run_wait_hook()
    step_message = 'Switch to next window'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_next_window()
    _append_screenshot()


def switch_to_parent_frame():
    """Switch to the parent of the current frame"""
    _run_wait_hook()
    step_message = 'Switch to parent frame'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to.parent_frame()
    _append_screenshot()


def switch_to_previous_window():
    """Switch to previous window/tab in the list of window handles.
    If current window is the first in the list of window handles this
    will circle back from the top.
    """
    _run_wait_hook()
    step_message = 'Switch to previous window'
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_previous_window()
    _append_screenshot()


def switch_to_window_by_index(index):
    """Switch to window/tab by index.
    Note: "The order in which the window handles are returned is arbitrary."

    Parameters:
    index : value
    """
    _run_wait_hook()
    step_message = 'Switch to window of index {}'.format(index)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_window_by_index(index)
    _append_screenshot()


def switch_to_window_by_partial_title(partial_title):
    """Switch to window/tab by partial title

    Parameters:
    partial_title : value
    """
    _run_wait_hook()
    step_message = 'Switch to window with partial title \'{}\''.format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_window_by_partial_title(partial_title)
    _append_screenshot()


def switch_to_window_by_partial_url(partial_url):
    """Switch to window/tab by partial URL

    Parameters:
    partial_url : value
    """
    _run_wait_hook()
    step_message = 'Switch to window with partial URL \'{}\''.format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_window_by_partial_url(partial_url)
    _append_screenshot()


def switch_to_window_by_title(title):
    """Switch to window/tab by title

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = 'Switch to window with title \'{}\''.format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_window_by_title(title)
    _append_screenshot()


def switch_to_window_by_url(url):
    """Switch to window/tab by URL

    Parameters:
    url : value
    """
    _run_wait_hook()
    step_message = 'Switch to window with URL \'{}\''.format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().switch_to_window_by_url(url)
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


def uncheck_element(checkbox):
    """Uncheck an checkbox element
    If checkbox is already unchecked this is is ignored.

    Parameters:
    checkbox : element
    """
    element = get_browser().find(checkbox)
    step_msg = 'Uncheck checkbox {}'.format(element.name)
    execution.logger.info(step_msg)
    _add_step(step_msg)
    get_browser().uncheck_element(element)
    _append_screenshot()


def verify_alert_is_not_present():
    """DEPRECATED, use verify_alert_not_present.
    Verify an alert is not present"""
    execution.logger.warning('verify_alert_is_not_present is DEPRECATED, use verify_alert_not_present')
    verify_alert_not_present()


def verify_alert_is_present():
    """DEPRECATED, use verify_alert_present"""
    execution.logger.warning('verify_alert_is_present is DEPRECATED, use verify_alert_present')
    verify_alert_present()


def assert_alert_not_present():
    """Verify an alert is not present"""
    step_message = 'Verify an alert is not present'
    execution.logger.info(step_message)
    _add_step(step_message)
    assert not get_browser().alert_is_present(), 'an alert was present'
    _append_screenshot()


def verify_alert_not_present():
    """Verify an alert is not present"""
    step_message = 'Verify an alert is not present'
    execution.logger.info(step_message)
    _add_step(step_message)
    if not get_browser().alert_is_present():
        _append_error('an alert was present')
    _append_screenshot()


def verify_alert_present():
    """Verify an alert is present"""
    step_message = 'Verify an alert is present'
    execution.logger.info(step_message)
    _add_step(step_message)
    assert get_browser().alert_is_present(), 'an alert was not present'
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


def verify_amount_of_windows(amount):
    """Verify the amount of open windows/tabs

    Parameters:
    amount : value
    """
    step_message = 'Verify amount of open windows is {}'.format(amount)
    execution.logger.info(step_message)
    _add_step(step_message)
    actual_amount = len(get_window_handles())
    error_msg = 'Expected {} windows but got {}'.format(amount, actual_amount)
    assert actual_amount == amount, error_msg
    _append_screenshot()


def verify_cookie_exists(name):
    """DEPRECATED, use verify_cookie_present
    Verify a cookie exists in the current session.
    The cookie is found by its name.

    Parameters:
    name: value
    """
    execution.logger.warning('verify_cookie_exists is DEPRECATED, use verify_cookie_present')
    verify_cookie_present(name)


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


def verify_cookie_value(name, value):
    """Verify the value of a cookie.

    Parameters:
    name: value
    value: value
    """
    _run_wait_hook()
    step_message = 'Verify that cookie "{}" value is "{}"'.format(name, value)
    execution.logger.info(step_message)
    _add_step(step_message)
    cookie = browser.get_browser().get_cookie(name)
    if not cookie:
        raise Exception('Cookie "{}" was not found'.format(name))
    elif not 'value' in cookie:
        raise Exception('Cookie "{}" did not have "value" key'.format(name))
    elif cookie['value'] != value:
        msg = ('Expected cookie "{}" value to be "{}" but was "{}"'
               .format(name, value, cookie['value']))
        raise Exception(msg)


def verify_element_attribute(element, attribute, value):
    """Verify value of element attribute

    Parameters:
    element : element
    attribute : value
    value : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} attribute {} value is {}'.format(element.name, attribute, value)
    execution.logger.info(step_message)
    _add_step(step_message)
    assert element.get_attribute(attribute) == value
    _append_screenshot()


def verify_element_attribute_is_not(element, attribute, value):
    """Verify the value of element attribute is not `value`

    Parameters:
    element : element
    attribute : value
    value : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Verify the element {} attribute {} value is not {}'.format(element.name, attribute, value)
    execution.logger.info(step_message)
    _add_step(step_message)
    assert element.get_attribute(attribute) != value
    _append_screenshot()


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
    msg = 'element {} is present'.format(element)
    assert not get_browser().element_is_present(element), msg


def verify_element_present(element):
    """Verify element is present in the DOM

    Parameters:
    element : element
    """
    _run_wait_hook()
    step_message = 'Verify element is present'
    execution.logger.info(step_message)
    _add_step(step_message)
    msg = 'element {} is not present'.format(element)
    assert get_browser().element_is_present(element), msg


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
    """DEPRECATED, use verify_element_present.
    Verify that en element exists.
    Parameters:
    element : element
    """
    execution.logger.warning('verify_exists is DEPRECATED, use verify_element_present')
    verify_element_present(element)


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
    _add_step(step_message)
    if not response.status_code == status_code:
        raise Exception("Expected response status code to be {0} but was {1}"
                        .format(status_code, response.status_code))


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


def verify_title_contains(partial_title):
    """Verify the page title contains text

    Parameters:
    partial_title : value
    """
    _run_wait_hook()
    step_message = "Verify page title contains '{}'".format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "expected title to contain '{}'".format(partial_title)
    assert partial_title in get_browser().title, error_msg
    _append_screenshot()


def verify_title_is_not(title):
    """Verify the page title is not the given value

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
    assert partial_url not in get_browser().current_url, error_msg
    _append_screenshot()


def verify_window_present_by_partial_title(partial_title):
    """Verify there is a window/tab present by partial title

    Parameters:
    partial_title : value
    """
    _run_wait_hook()
    step_message = "Verify window present by partial title '{}'".format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "There is no window present with partial title '{}'".format(partial_title)
    window_titles = get_browser().get_window_titles()
    assert any(partial_title in t for t in window_titles), error_msg
    _append_screenshot()


def verify_window_present_by_partial_url(partial_url):
    """Verify there is a window/tab present by partial URL

    Parameters:
    partial_url : value
    """
    _run_wait_hook()
    step_message = "Verify window present by partial URL '{}'".format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    urls = get_browser().get_window_urls()
    error_msg = "There is no window present with partial URL '{}'".format(partial_url)
    assert any(partial_url in url for url in urls), error_msg
    _append_screenshot()


def verify_window_present_by_title(title):
    """Verify there is a window/tab present by title

    Parameters:
    title : value
    """
    _run_wait_hook()
    step_message = "Verify window present by title '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "There is no window present with title '{}'".format(title)
    assert title in get_browser().get_window_titles(), error_msg
    _append_screenshot()


def verify_window_present_by_url(url):
    """Verify there is a window/tab present by URL

    Parameters:
    url : value
    """
    _run_wait_hook()
    step_message = "Verify window present by URL '{}'".format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    error_msg = "There is no window present with URL '{}'".format(url)
    assert url in get_browser().get_window_urls(), error_msg
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
        raise ValueError('seconds value should be a number')
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


def wait_for_element_displayed(element, timeout=30):
    """Wait for element to be present and displayed

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to be displayed'.format(element)
    execution.logger.info(step_message)
    get_browser().wait_for_element_displayed(element, timeout)
    _append_screenshot()


def wait_for_element_enabled(element, timeout=30):
    """Wait for element to be enabled

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Wait for element {} to be enabled'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_enabled(element, timeout)
    _append_screenshot()


def wait_for_element_has_attribute(element, attribute, timeout=30):
    """Wait for element to have attribute

    Parameters:
    element : element
    attribute : attribute
    timeout (30) : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Wait for element {} to have {} attribute'.format(element.name, attribute)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_has_attribute(element, attribute, timeout)
    _append_screenshot()


def wait_for_element_has_not_attribute(element, attribute, timeout=30):
    """Wait for element to not have attribute

    Parameters:
    element : element
    attribute : attribute
    timeout (30) : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Wait for element {} to not have {} attribute'.format(element.name, attribute)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_has_not_attribute(element, attribute, timeout)
    _append_screenshot()


def wait_for_element_not_displayed(element, timeout=30):
    """Wait for element to be not displayed

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to be not displayed'.format(element)
    execution.logger.info(step_message)
    get_browser().wait_for_element_not_displayed(element, timeout)


def wait_for_element_not_enabled(element, timeout=30):
    """Wait for element to be not enabled.

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    element = get_browser().find(element, timeout=0)
    step_message = 'Wait for element {} to be not enabled'.format(element.name)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_not_enabled(element, timeout)
    _append_screenshot()


def wait_for_element_not_exist(element, timeout=20):
    """DEPRECATED, use wait_for_element_not_present
    Wait for a webelement to stop existing in the DOM.

    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    execution.logger.warning('wait_for_element_not_exists is DEPRECATED, use wait_for_element_not_present')
    wait_for_element_not_present()


def wait_for_element_not_present(element, timeout=30):
    """Wait for element to stop being present in the DOM.
    If element is not present, this will be ignored.

    Parameters:
    element : element
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to be not present'.format(element)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_not_present(element, timeout)
    _append_screenshot()


def wait_for_element_not_visible(element, timeout=20):
    """DEPRECATED, use wait_for_element_not_displayed

    Wait for an element to stop being visible.
    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    execution.logger.warning('wait_for_element_not_visible is DEPRECATED, use wait_for_element_not_displayed')
    wait_for_element_not_displayed(element, timeout)


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


def wait_for_element_text(element, text, timeout=30):
    """Wait for element text to match given text

    Parameters:
    element : element
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} text to be \'{}\''.format(element, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_text(element, text, timeout)
    _append_screenshot()


def wait_for_element_text_contains(element, text, timeout=30):
    """Wait for element to contain text

    Parameters:
    element : element
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to contain text \'{}\''.format(element, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_text_contains(element, text, timeout)
    _append_screenshot()


def wait_for_element_text_is_not(element, text, timeout=30):
    """Wait for element text to not match given text

    Parameters:
    element : element
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} text to not be \'{}\''.format(element, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_text_is_not(element, text, timeout)
    _append_screenshot()


def wait_for_element_text_not_contains(element, text, timeout=30):
    """Wait for element to not contain text

    Parameters:
    element : element
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = 'Wait for element {} to not contain text \'{}\''.format(element, text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_element_text_not_contains(element, text, timeout)
    _append_screenshot()


def wait_for_element_visible(element, timeout=20):
    """DEPRECATED, use wait_for_element_displayed

    Wait for element to be visible.
    Parameters:
    element : element
    timeout (optional, default: 20) : value
    """
    execution.logger.warning('wait_for_element_visible is DEPRECATED, use wait_for_element_displayed')
    wait_for_element_displayed(element, timeout)


def wait_for_page_contains_text(text, timeout=30):
    """Wait for page contains text in the DOM

    Parameters:
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for page contains text '{}'".format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_page_contains_text(text, timeout)
    _append_screenshot()


def wait_for_page_not_contains_text(text, timeout=30):
    """Wait for page to not contain text in the DOM

    Parameters:
    text : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for page to not contain text '{}'".format(text)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_page_not_contains_text(text, timeout)
    _append_screenshot()


def wait_for_title(title, timeout=30):
    """Wait for page title to be the given title

    Parameters:
    title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for title to be '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_title(title, timeout)
    _append_screenshot()


def wait_for_title_contains(partial_title, timeout=30):
    """Wait for page title to contain partial_title

    Parameters:
    partial_title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for title to contain '{}'".format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_title_contains(partial_title, timeout)
    _append_screenshot()


def wait_for_title_is_not(title, timeout=30):
    """Wait for page title to not be the given title

    Parameters:
    title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for title to not be '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_title_is_not(title, timeout)
    _append_screenshot()


def wait_for_title_not_contains(partial_title, timeout=30):
    """Wait for page title to not contain partial_title

    Parameters:
    partial_title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for title to not contain '{}'".format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_title_not_contains(partial_title, timeout)
    _append_screenshot()


def wait_for_window_present_by_partial_title(partial_title, timeout=30):
    """Wait for window/tab present by partial title

    Parameters:
    partial_title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for window present by partial title '{}'".format(partial_title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_window_present_by_partial_title(partial_title, timeout)
    _append_screenshot()


def wait_for_window_present_by_partial_url(partial_url, timeout=30):
    """Wait for window/tab present by partial url

    Parameters:
    partial_url : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for window present by partial url '{}'".format(partial_url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_window_present_by_partial_url(partial_url, timeout)
    _append_screenshot()


def wait_for_window_present_by_title(title, timeout=30):
    """Wait for window/tab present by title

    Parameters:
    title : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for window present by title '{}'".format(title)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_window_present_by_title(title, timeout)
    _append_screenshot()


def wait_for_window_present_by_url(url, timeout=30):
    """Wait for window/tab present by url

    Parameters:
    url : value
    timeout (30) : value
    """
    _run_wait_hook()
    step_message = "Wait for window present by url '{}'".format(url)
    execution.logger.info(step_message)
    _add_step(step_message)
    get_browser().wait_for_window_present_by_url(url, timeout)
    _append_screenshot()
