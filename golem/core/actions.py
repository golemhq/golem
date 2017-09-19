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
import requests

from golem import core
from golem.core import execution_logger as logger
from golem.core.exceptions import TextNotPresent, ElementNotFound
from golem.selenium.utils import get_driver


def _run_wait_hook():
    wait_hook = core.get_setting('wait_hook')
    if wait_hook:
        time.sleep(0.3)
        start_time = time.time()
        extend_module = importlib.import_module('projects.{0}.extend'
                                                .format(core.project))
        wait_hook_function = getattr(extend_module, wait_hook)
        wait_hook_function()
        logger.logger.debug('Wait hook waited for {} seconds'
                            .format(time.time() - start_time))


# def _wait_for_visible(element):
#     not_visible = True
#     start_time = time.time()
#     visible = element.is_displayed()
#     while not visible:
#         print('Element is not visible, waiting..')
#         time.sleep(0.5)
#         visible = element.is_displayed()


# def force_click(css_selector):
#     driver = core.get_or_create_web_driver()
#     click_script = """$("{0}").click();""".format(css_selector)
#     print click_script
#     driver.execute_script(click_script)


def _capture_or_add_step(message, screenshot_on_step):
    if screenshot_on_step:
        capture(message)
    else:
        step(message)


def capture(message=''):
    _run_wait_hook() 
    logger.logger.info('Take screenshot {}'.format(message))
    driver = get_driver()
    # print('SHOULD SAVE SCREENSHOT IN', core.report_directory)
    
    # store img in memory and save to disk when at the end
    # when the report is generated
    # Note: this solution uses pillow
    # img = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
    # img_id = str(uuid.uuid4())[:8]
    # logger.screenshots[img_id] = img
    
    # store image at this point, the target directory is already
    # created since the beginning of the test, stored in golem.gore.report_directory
    img_id = str(uuid.uuid4())[:8]
    img_path = os.path.join(core.report_directory, '{}.png'.format(img_id))
    driver.get_screenshot_as_file(img_path)

    full_message = '{0}__{1}'.format(message, img_id)
    step(full_message)


def click(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Click {0}'.format(webelement.name)
    webelement.click()
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def close():
    logger.logger.info('Close driver')
    driver = get_driver()
    driver.quit()
    core.reset_driver_object()


def debug():
    print('Entering interactive debug mode')
    print('Type exit to stop')
    command = input()
    while command != 'exit':
        print('running {}'.format(command))
        eval(command)
        command = input()


def mouse_hover(element):
    _run_wait_hook()
    driver = get_driver()
    webelement = driver.find(element)
    step_message = 'Mouse hover element \'{0}\''.format(webelement.name)
    logger.logger.info(step_message)
    ActionChains(driver).move_to_element(webelement).perform()
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def navigate(url):
    step_message = 'Navigate to: \'{0}\''.format(url)
    driver = get_driver()
    driver.get(url)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def press_key(element, key):
    step_message = 'Press key: {}'.format(key)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    webelement = get_driver().find(element)
    if key == 'RETURN' or key == 'ENTER':
        webelement.send_keys(Keys.RETURN);
    else:
        raise Exception('Key value is invalid')


def random(value):
    random_string = ''
    for char in value:
        if char == 'c':
            random_string += rand.choice(string.ascii_lowercase)
        elif char == 'd':
            random_string += str(rand.randint(0, 9))
        else:
            random_string += char
    logger.logger.info('Random value generated: {}'.format(random_string))
    return random_string


def select_by_index(element, index):
    _run_wait_hook()
    webelement = get_driver.find(element)
    step_message = 'Select option of index {0} from element {1}'.format(index, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_index(index)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_text(element, text):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Select \'{0}\' from element {1}'.format(text, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_visible_text(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_value(element, value):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Select \'{0}\' value from element {1}'.format(value, webelement.name)
    select = selenium.webdriver.support.select.Select(webelement)
    select.select_by_value(value)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def send_keys(element, text):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Write \'{0}\' in element {1}'.format(text, webelement.name)
    webelement.send_keys(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def step(message):
    logger.steps.append(message)


def store(key, value):
    logger.logger.info('Store value {} in key {}'.format(value, key))
    # core.test_data[key] = value
    setattr(core.test_data, key, value)

# TO DO
def verify_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element exists'
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    try:
        webelement = get_driver().find(element, timeout=1)
    except:
        raise ElementNotFound('Element {} does not exist'.format(element))


def verify_is_enabled(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is enabled'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not webelement.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_enabled(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is not enabled'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if webelement.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_selected(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is not selected'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if webelement.is_selected():
        raise Exception('Element is selected')


def verify_is_not_visible(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is not visible'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if webelement.is_displayed():
        raise Exception('Element is visible')


def verify_is_selected(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is selected'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not webelement.is_selected():
        raise Exception('Element is not selected')


def verify_is_visible(element):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify the element \'{0}\' is visible'.format(webelement.name)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not webelement.is_displayed():
        raise Exception('Element is not visible')


def verify_not_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element'
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    try:
        webelement = get_driver().find(element)
        if webelement:
            raise Exception('Element {} exists and should not'
                            .format(webelement.name))
    except ElementNotFound:
        pass


def verify_selected_option(element, text):
    _run_wait_hook()
    webelement = get_driver().find(element)
    select = selenium.webdriver.support.select.Select(webelement)
    step_message = 'Verify selected option of element \'{0}\' is \'{1}\''.format(
                   webelement.name, text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(webelement.name, text))


def verify_text(text):
    _run_wait_hook()
    driver = get_driver()
    step_message = 'Verify \'{0}\' is present in page'.format(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in driver.page_source:
        raise TextNotPresent(
                    "Text '{}' was not found in the page".format(text))


def verify_text_in_element(element, text):
    _run_wait_hook()
    webelement = get_driver().find(element)
    step_message = 'Verify element \'{0}\' contains text \'{1}\''.format(webelement.name, text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in webelement.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}"
                             .format(text, webelement.name))


def wait(seconds):
    logger.logger.info('Waiting for {} seconds'.format(seconds))
    try:
        to_float = float(seconds)
    except:
        raise Exception('seconds value should be a number')
    time.sleep(to_float)


def wait_for_element_not_visible(element, timeout=20):
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    logger.logger.info('Waiting for element {} to be not visible'.format(element))
    start_time = time.time()
    timed_out = False
    webelement = get_driver().find(element)
    while webelement.is_displayed() and not timed_out:
        logger.logger.debug('Element is still visible, waiting..')
        time.sleep(0.5)
        if time.time() - start_time > timeout:
            timed_out = True


def wait_for_element_visible(element, timeout=20):
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    _run_wait_hook()
    logger.logger.info('Waiting for element {} to be visible'.format(element))
    start_time = time.time()
    timed_out = False
    webelement = get_driver().find(element)
    while not webelement.is_displayed() and not timed_out:
        logger.logger.debug('Element is not visible, waiting..')
        time.sleep(0.5)
        if time.time() - start_time > timeout:
            timed_out = True


def wait_for_element_enabled(element, timeout=20):
    logger.logger.info('Waiting for element {} to be enabled'.format(element))
    start_time = time.time()
    timed_out = False
    webelement = get_driver().find(element)
    enabled = webelement.is_enabled()
    while not enabled:
        logger.logger.debug('Element is not enabled, waiting..')
        time.sleep(0.5)
        enabled = webelement.is_displayed()
        if time.time() - start_time > timeout:
            timed_out = True


def get(url, headers={}, params={}):
    step_message = 'Make GET request to {}'.format(url)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.get(url, headers=headers, params=params)
    store('last_response', response)


def post(url, headers={}, data={}):
    step_message = 'Make POST request to {}'.format(url)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    response = requests.post(url, data)
    store('last_response', response)


def verify_response_status_code(response, status_code):
    if type(status_code) == str:
        if status_code.isdigit():
            status_code = int(status_code)
    step_message = 'Verify response status code is {}'.format(status_code)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, False)
    if not response.status_code == status_code:
        raise Exception("Expected response status code to be {0} but was {1}"
                        .format(status_code, response.status_code))


def verify_response_content():
    pass

