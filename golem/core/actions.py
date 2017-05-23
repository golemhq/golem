# -*- coding: utf-8 -*-
import time
import uuid
import io
import importlib
import string
import random as rand

import selenium
from PIL import Image

from golem import core
from golem.core import execution_logger as logger
from golem.core.exceptions import TextNotPresent, ElementNotFound
from golem.core.selenium_utils import get_selenium_object


def _run_wait_hook():
    wait_hook = core.get_setting('wait_hook')
    if wait_hook:
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
#     driver = core.getOrCreateWebdriver()
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
    driver = core.getOrCreateWebdriver()
    #screenshot_name = 'test' + msg.replace(' ', '_')
    #screenshot_filename = .format(len(logger.screenshots))
    #driver.save_screenshot(screenshot_name + '.jpg')
    img = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
    img_id = str(uuid.uuid4())[:8]
    logger.screenshots[img_id] = img
    full_message = '{0}__{1}'.format(message, img_id)
    add_step(full_message)


def click(element):
    step_message = 'Click {0}'.format(element[2])
    _run_wait_hook()    
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    #_wait_for_visible(test_object)
    test_object.click()
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def close():
    driver = core.getOrCreateWebdriver()
    driver.quit()
    core.reset_driver_object()


def go_to(url):
    step_message = 'Go to url:\'{0}\''.format(url)
    driver = core.getOrCreateWebdriver()
    driver.get(url)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def random(*args):
    random_string = ''
    for arg in args:
        if arg[0] == 'c':
            string_length = int(arg[1:])
            new_str = ''.join(rand.sample(string.ascii_lowercase,
                                            string_length))
            random_string += new_str
        elif arg[0] == 'd':
            string_length = int(arg[1:])
            new_str = rand.randint(pow(10, string_length - 1),
                                   pow(10, string_length) - 1)
            random_string += str(new_str)
        else:
            random_string += arg
    return random_string


def select_by_index(element, index):
    step_message = 'Select option of index {0} from element {1}'.format(index, element[2])
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_index(index)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_text(element, text):
    step_message = 'Select \'{0}\' from element {1}'.format(text, element[2])
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_visible_text(text)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def select_by_value(element, value):
    step_message = 'Select \'{0}\' value from element {1}'.format(value, element[2])
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_value(value)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def send_keys(element, text):
    step_message = 'Write \'{0}\' in element {1}'.format(text, element[2])
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    test_object.send_keys(text)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])


def store(key, value):
    core.test_data[key] = value


def verify_exists(element):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    step_message = 'Verify that the element {} exists'.format(element[2])
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    test_object = get_selenium_object(element, driver)


def verify_is_enabled(element):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    step_message = 'Verify the element \'{0}\' is enabled'.format(element[2])
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not test_object.is_enabled():
        raise Exception('Element is enabled')


def verify_is_not_enabled(element):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    step_message = 'Verify the element \'{0}\' is not enabled'.format(element[2])
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if test_object.is_enabled():
        raise Exception('Element is enabled')


def verify_not_exists(element):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    step_message = 'Verify that the element {} does not exists'.format(element[2])
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    try:
        test_object = get_selenium_object(element, driver)
        if test_object:
            raise Exception('Element {} exists and should not'
                            .format(element[2]))
    except ElementNotFound:
        pass


def verify_selected_option(element, text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    step_message = 'Verify selected option of element \'{0}\' is \'{1}\''.format(element[2], text)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(element[2], text))


def verify_text(text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    step_message = 'Verify \'{0}\' is present in page'.format(text)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in driver.page_source:
        raise TextNotPresent(
                    "Text '{}' was not found in the page".format(text))


def verify_text_in_element(element, text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    step_message = 'Verify element \'{0}\' contains text \'{1}\''.format(element[2], text)
    _capture_or_add_step(step_message, core.settings['screenshot_on_step'])
    if text not in test_object.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}"
                             .format(text, element[2]))


def wait(seconds):
    try:
        to_int = int(seconds)
    except:
        raise Exception('seconds value should be an integer')
    time.sleep(to_int)


def wait_for_element_visible(element, timeout=20):
    start_time = time.time()
    timed_out = False
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    visible = test_object.is_displayed()
    while not visible and not timed_out:
        print('Element is not visible, waiting..')
        time.sleep(0.5)
        visible = test_object.is_displayed()
        current_time = time.time()
        if current_time - start_time > timeout:
            timed_out = True


def wait_for_element_enabled(element, timeout=20):
    start_time = time.time()
    timed_out = False
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    enabled = element.is_enabled()
    while not enabled:
        print('Element is not enabled, waiting..')
        time.sleep(0.5)
        enabled = element.is_displayed()
        current_time = time.time()
        if current_time - start_time > timeout:
            timed_out = True
