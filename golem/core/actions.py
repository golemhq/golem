"""Function wrappers for the actions"""
import time
import uuid
# import io
import os
import importlib
import string
import random as rand

import selenium
from selenium.webdriver.common.keys import Keys
#from PIL import Image

from golem import core
from golem.core import execution_logger as logger
from golem.core.exceptions import TextNotPresent, ElementNotFound
from golem.selenium.utils import get_selenium_object


def _run_wait_hook():
    wait_hook = core.get_setting('wait_hook')
    if wait_hook:
        wait('0.3')
        start_time = time.time()
        extend_module = importlib.import_module('projects.{0}.extend'
                                                .format(core.project))
        wait_hook_function = getattr(extend_module, wait_hook)
        wait_hook_function()
        print('Wait hook waited for {} seconds'.format(time.time() - start_time))


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
        add_step(message)


def add_step(message):
    logger.steps.append(message)


def capture(message=''):
    _run_wait_hook() 
    logger.logger.info('Take screenshot {}'.format(message))
    driver = core.get_or_create_webdriver()
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
    add_step(full_message)


def click(element):
    _run_wait_hook()
    step_message = 'Click {0}'.format(element[2])
    element = get_selenium_object(element)
    element.click()
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def close():
    logger.logger.info('Close driver')
    driver = core.get_or_create_webdriver()
    driver.quit()
    core.reset_driver_object()


def go_to(url):
    step_message = 'Go to url: \'{0}\''.format(url)
    driver = core.get_or_create_webdriver()
    driver.get(url)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def press_key(element, key):
    step_message = 'Press key: {}'.format(key)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    element = get_selenium_object(element)
    if key == 'RETURN' or key == 'ENTER':
        element.send_keys(Keys.RETURN);
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
    step_message = 'Select option of index {0} from element {1}'.format(index, element[2])
    _run_wait_hook()
    test_object = get_selenium_object(element)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_index(index)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_text(element, text):
    step_message = 'Select \'{0}\' from element {1}'.format(text, element[2])
    _run_wait_hook()
    test_object = get_selenium_object(element)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_visible_text(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_value(element, value):
    step_message = 'Select \'{0}\' value from element {1}'.format(value, element[2])
    _run_wait_hook()
    test_object = get_selenium_object(element)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_value(value)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def send_keys(element, text):
    _run_wait_hook()
    step_message = 'Write \'{0}\' in element {1}'.format(text, element[2])
    element = get_selenium_object(element)
    element.send_keys(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def store(key, value):
    logger.logger.info('Store value {} in key {}'.format(value, key))
    core.test_data[key] = value


def verify_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element {} exists'.format(element[2])
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    test_object = get_selenium_object(element)


def verify_is_enabled(element):
    _run_wait_hook()
    test_object = get_selenium_object(element)
    step_message = 'Verify the element \'{0}\' is enabled'.format(element[2])
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not test_object.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_enabled(element):
    _run_wait_hook()
    test_object = get_selenium_object(element)
    step_message = 'Verify the element \'{0}\' is not enabled'.format(element[2])
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if test_object.is_enabled():
        raise Exception('Element is enabled')


def verify_not_exists(element):
    _run_wait_hook()
    step_message = 'Verify that the element {} does not exists'.format(element[2])
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    try:
        test_object = get_selenium_object(element)
        if test_object:
            raise Exception('Element {} exists and should not'
                            .format(element[2]))
    except ElementNotFound:
        pass


def verify_selected_option(element, text):
    _run_wait_hook()
    test_object = get_selenium_object(element)
    select = selenium.webdriver.support.select.Select(test_object)
    step_message = 'Verify selected option of element \'{0}\' is \'{1}\''.format(element[2], text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(element[2], text))


def verify_text(text):
    _run_wait_hook()
    driver = core.get_or_create_webdriver()
    step_message = 'Verify \'{0}\' is present in page'.format(text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in driver.page_source:
        raise TextNotPresent(
                    "Text '{}' was not found in the page".format(text))


def verify_text_in_element(element, text):
    _run_wait_hook()
    test_object = get_selenium_object(element)
    step_message = 'Verify element \'{0}\' contains text \'{1}\''.format(element[2], text)
    logger.logger.info(step_message)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in test_object.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}"
                             .format(text, element[2]))


def wait(seconds):
    logger.logger.info('Waiting for {} seconds'.format(seconds))
    try:
        to_int = int(seconds)
    except:
        raise Exception('seconds value should be an integer')
    time.sleep(to_int)


def wait_for_element_not_visible(element, timeout=20):
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    logger.logger.info('Waiting for element {} to be not visible'.format(element))
    start_time = time.time()
    timed_out = False
    test_object = get_selenium_object(element)
    visible = test_object.is_displayed()
    while visible and not timed_out:
        logger.logger.debug('Element is still visible, waiting..')
        time.sleep(0.5)
        visible = test_object.is_displayed()
        current_time = time.time()
        if current_time - start_time > timeout:
            timed_out = True


def wait_for_element_visible(element, timeout=20):
    try:
        timeout = int(timeout)
    except:
        raise Exception('Timeout should be digits only')
    logger.logger.info('Waiting for element {} to be not visible'.format(element))
    start_time = time.time()
    timed_out = False
    test_object = get_selenium_object(element)
    visible = test_object.is_displayed()
    while not visible and not timed_out:
        logger.logger.debug('Element is not visible, waiting..')
        time.sleep(0.5)
        visible = test_object.is_displayed()
        current_time = time.time()
        if current_time - start_time > timeout:
            timed_out = True


def wait_for_element_enabled(element, timeout=20):
    logger.logger.info('Waiting for element {} to be enabled'.format(element))
    start_time = time.time()
    timed_out = False
    test_object = get_selenium_object(element)
    enabled = element.is_enabled()
    while not enabled:
        logger.logger.debug('Element is not enabled, waiting..')
        time.sleep(0.5)
        enabled = element.is_displayed()
        current_time = time.time()
        if current_time - start_time > timeout:
            timed_out = True


