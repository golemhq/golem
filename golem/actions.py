"""Function wrappers for the actions"""
import time
import uuid
import os
import importlib
import string
import random as rand

import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import requests

from golem.core.exceptions import TextNotPresent, ElementNotFound
from golem.browser import get_browser
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


def _capture_or_add_step(message, screenshot_on_step):
    if screenshot_on_step:
        capture(message)
    else:
        step(message)


def assert_contains(element, value):
    step_message = 'Assert that {0} contains {1}'.format(element, value)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not value in element:
        raise Exception('Expected {} to contain {}'.format(element, value))


def assert_equals(actual_value, expected_value):
    step_message = 'Assert that {0} equals {1}'.format(actual_value, expected_value)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not actual_value == expected_value:
        raise Exception('Expected {} to equal {}'.format(actual_value, expected_value))


def assert_false(condition):
    step_message = 'Assert that {0} is false'.format(condition)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if condition:
        raise Exception('Expected {} to be false'.format(condition))


def assert_true(condition):
    step_message = 'Assert that {0} is true'.format(condition)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not condition:
        raise Exception('Expected {} to be true'.format(condition))


def capture(message=''):
    _run_wait_hook()
    execution.logger.info('Take screenshot {}'.format(message))
    driver = get_browser()
    # store image at this point, the target directory is already
    # created since the beginning of the test, stored in golem.core.report_directory
    img_id = str(uuid.uuid4())[:8]
    img_path = os.path.join(execution.report_directory, '{}.png'.format(img_id))
    driver.get_screenshot_as_file(img_path)

    if len(message) == 0:
        message = 'Screenshot'

    full_message = '{0}__{1}'.format(message, img_id)
    step(full_message)


def clear(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Clear {0} element'.format(webelement.name)
    execution.logger.info(step_message)
    webelement.clear()
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def click(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Click {0}'.format(webelement.name)
    execution.logger.info(step_message)
    webelement.click()
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def close():
    execution.logger.info('Close driver')
    driver = get_browser()
    driver.quit()
    execution.browser = None


def debug():
    import readline  # optional, will allow Up/Down/History in the console
    import code
    def console_exit():
        raise SystemExit
    vars_copy = globals().copy()
    vars_copy.update(locals())
    vars_copy['exit'] = console_exit
    banner = 'Entering interactive debug mode\nType exit() to stop'
    shell = code.InteractiveConsole(vars_copy)
    try:
        shell.interact(banner=banner)
    except SystemExit:
        pass


def get(url):
    navigate(url)


def mouse_hover(element):
    _run_wait_hook()
    driver = get_browser()
    webelement = driver.find(element)
    step_message = 'Mouse hover element \'{0}\''.format(webelement.name)
    execution.logger.info(step_message)
    ActionChains(driver).move_to_element(webelement).perform()
    #_capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def navigate(url):
    step_message = 'Navigate to: \'{0}\''.format(url)
    driver = get_browser()
    driver.get(url)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    
    
def press_key(element, key):
    step_message = 'Press key: {}'.format(key)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    webelement = get_browser().find(element)
    if key == 'RETURN' or key == 'ENTER':
        webelement.send_keys(Keys.RETURN)
    elif key == 'UP':
        webelement.send_keys(Keys.UP)
    elif key == 'DOWN':
        webelement.send_keys(Keys.DOWN)
    elif key == 'LEFT':
        webelement.send_keys(Keys.LEFT)
    elif key == 'RIGHT':
        webelement.send_keys(Keys.RIGHT)
    else:
        raise Exception('Key value {} is invalid'.format(key))


def random(value):
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
    _run_wait_hook()
    step_message = 'Refresh page'
    get_browser().refresh()
    #get_browser().execute_script("location.reload()")
    #browser = get_browser()
    #browser.get(browser.current_url);
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def select_by_index(element, index):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Select option of index {0} from element {1}'.format(index, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_index(index)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def select_by_text(element, text):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Select \'{0}\' from element {1}'.format(text, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_visible_text(text)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def select_by_value(element, value):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Select \'{0}\' value from element {1}'.format(value, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_value(value)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def send_keys(element, text):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Write \'{0}\' in element {1}'.format(text, webelement.name)
    # TODO chrome driver drops some characters when calling send_keys
    # if execution.browser_name in ['chrome', 'chrome-headless', 'chrome-remote']:
    #     for c in text:
    #         webelement.send_keys(c)
    #         time.sleep(0.1)
    # else:
    webelement.send_keys(text)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def set_window_size(width, height):
    _run_wait_hook()
    browser = get_browser()
    step_message = 'Set browser window size to {0}x, {1}y.'.format(width, height)
    browser.set_window_size(width, height)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])


def step(message):
    execution.steps.append(message)


def store(key, value):
    execution.logger.info('Store value {} in key {}'.format(value, key))
    setattr(execution.data, key, value)


# TODO rename to verify_element_exists
def verify_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element exists'
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    try:
        webelement = get_browser().find(element, timeout=1)
    except:
        raise ElementNotFound('Element {} does not exist'.format(element))


def verify_is_enabled(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is enabled'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if not webelement.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_enabled(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is not enabled'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if webelement.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_selected(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is not selected'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if webelement.is_selected():
        raise Exception('Element is selected')


def verify_is_not_visible(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is not visible'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if webelement.is_displayed():
        raise Exception('Element is visible')


def verify_is_selected(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is selected'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if not webelement.is_selected():
        raise Exception('Element is not selected')


def verify_is_visible(element):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify the element \'{0}\' is visible'.format(webelement.name)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if not webelement.is_displayed():
        raise Exception('Element is not visible')


def verify_not_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element'
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    try:
        webelement = get_browser().find(element)
        if webelement:
            raise Exception('Element {} exists and should not'
                            .format(webelement.name))
    except ElementNotFound:
        pass


def verify_selected_option(element, text):
    _run_wait_hook()
    webelement = get_browser().find(element)
    select = selenium.webdriver.support.select.Select(webelement)
    step_message = ('Verify selected option of element \'{0}\''
                    ' is \'{1}\''.format(webelement.name, text))
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(webelement.name, text))


def verify_text(text):
    _run_wait_hook()
    driver = get_browser()
    step_message = 'Verify \'{0}\' is present in page'.format(text)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if text not in driver.page_source:
        raise TextNotPresent("Text '{}' was not found in the page".format(text))


def verify_text_in_element(element, text):
    _run_wait_hook()
    webelement = get_browser().find(element)
    step_message = 'Verify element \'{0}\' contains text \'{1}\''.format(webelement.name, text)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, execution.settings['screenshot_on_step'])
    if text not in webelement.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}. Text \'{2}\' was found."
                             .format(text, webelement.name, webelement.text))


def wait(seconds):
    execution.logger.info('Waiting for {} seconds'.format(seconds))
    try:
        to_float = float(seconds)
    except:
        raise Exception('seconds value should be a number')
    time.sleep(to_float)

# TODO
# def wait_for_element_exists(element, timeout=20):
# #     try:
# #         timeout = int(timeout)
# #     except:
# #         raise Exception('Timeout should be digits only')
# #     execution.logger.info('Waiting for element {} to not exist'.format(element))
# #     webelement = None
# #     start_time = time.time()
# #     while not webelement and (time.time() - start_time) < timeout:
# #         try:
# #             webelement = get_browser().find(element, timeout=3)
# #         except:
# #             print('wait_for_element_exists')

#     start_time = time.time()
#     still_exists = True
#     remaining_time = time.time() - start_time
#     while still_exists and remaining_time < timeout:
#         time.sleep(0.5)
#         remaining_time = time.time() - start_time
#         try:
#             webelement = get_browser().find(element, timeout=0)
#         except:
#             still_exists = False
#     # else:
#     #     execution.logger.debug('Element {} was not found, continuing...'.format(element)) 


# def wait_for_element_clickable(element, timeout=20):
#     browser = get_browser()
#     element = WebDriverWait(browser, timeout).until(
#         EC.element_to_be_clickable())



def wait_for_element_not_exist(element, timeout=20):
    """wait for a webelement to stop existing in the DOM.
    
    Wait for a webelement to stop existing in the DOM or until
    the timeout ends. If the webelement still exists after the time
    ended it will not raise an exception.
    """
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    execution.logger.info('Waiting for element {} to not exist'.format(element))
    webelement = None
    try:
        s = get_browser().find(element, timeout=3)
    except:
        execution.logger.debug('Element already does not exist, continuing...')
        return
    start_time = time.time()
    still_exists = True
    remaining_time = time.time() - start_time
    while still_exists and remaining_time <= timeout:
        execution.logger.debug('Element still exists in the DOM, waiting...')
        time.sleep(0.5)
        remaining_time = time.time() - start_time
        try:
            webelement = get_browser().find(element, timeout=0)
        except:
            still_exists = False
            execution.logger.debug('Element stopped existing')


def wait_for_element_not_visible(element, timeout=20):
    """wait for a webelement to stop being visible (is_displayed() == True)."""
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    execution.logger.info('Waiting for element {} to be not visible'.format(element))
    webelement = None
    try:
        webelement = get_browser().find(element, timeout=3)
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


def wait_for_element_enabled(element, timeout=20):
    execution.logger.info('Waiting for element {} to be enabled'.format(element))
    start_time = time.time()
    timed_out = False
    #webelement = None
    #try:
    webelement = get_browser().find(element, timeout)
    enabled = webelement.is_enabled()
    while not enabled and not timed_out:
        execution.logger.debug('Element is not enabled, waiting..')
        time.sleep(0.5)
        enabled = webelement.is_displayed()
        if time.time() - start_time > timeout:
            timed_out = True



def wait_for_element_visible(element, timeout=20):
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    _run_wait_hook()
    execution.logger.info('Waiting for element {} to be visible'.format(element))
    start_time = time.time()
    timed_out = False
    webelement = get_browser().find(element)
    while not webelement.is_displayed() and not timed_out:
        execution.logger.debug('Element is not visible, waiting..')
        time.sleep(0.5)
        if time.time() - start_time > timeout:
            timed_out = True


def http_get(url, headers={}, params={}, verify_ssl_cert=True):
    step_message = 'Make GET request to {}'.format(url)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.get(url, headers=headers, params=params, verify=verify_ssl_cert)
    store('last_response', response)


def http_post(url, headers={}, data={}, verify_ssl_cert=True):
    step_message = 'Make POST request to {}'.format(url)
    execution.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.post(url, headers=headers, data=data, verify=verify_ssl_cert)
    store('last_response', response)


def verify_response_status_code(response, status_code):
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
