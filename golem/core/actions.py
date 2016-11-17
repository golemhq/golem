# -*- coding: utf-8 -*-
import time
import uuid
import StringIO
import importlib

import selenium
from PIL import Image

from golem import core
from golem.core import execution_logger as logger
from golem.core.exceptions import TextNotPresent
from golem.core.selenium_utils import get_selenium_object


def _add_step(msg, screenshot=None):
    if screenshot:
        msg += '__{}'.format(screenshot)
    logger.steps.append(msg)


def _run_wait_hook():
    wait_hook = core.get_setting('wait_hook')
    if wait_hook:
        start_time = time.time()
        extend_module = importlib.import_module('projects.{0}.extend'
                                                .format(core.project))
        wait_hook_function = getattr(extend_module, wait_hook)
        wait_hook_function()
        print 'Wait hook waited for {} seconds'.format(time.time() - start_time)


def _wait_for_visible(element):
    not_visible = True
    start_time = time.time()
    visible = element.is_displayed()        
    while not visible:
        print 'Element is not visible, waiting..'
        time.sleep(0.5)
        visible = element.is_displayed()


def force_click(css_selector):
    driver = core.getOrCreateWebdriver()
    click_script = """$("{0}").click();""".format(css_selector)
    print click_script
    driver.execute_script(click_script)


def click(obj):
    _run_wait_hook()    
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    _wait_for_visible(test_object)
    test_object.click()
    _add_step('Click {0}'.format(obj[2]))


def go_to(url):
    driver = core.getOrCreateWebdriver()
    driver.get(url)
    _add_step('Go to url:\'{0}\''.format(url))


def send_keys(obj, text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    test_object.send_keys(text)
    _add_step('Write \'{0}\' in element {1}'.format(text, obj[2]))


def select_by_text(obj, text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_visible_text(text)
    _add_step('Select \'{0}\' from element {1}'.format(text, obj[2]))


def select_by_index(obj, index):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_index(index)
    _add_step('Select index \'{0}\' in element {1}'.format(index, obj[2]))


def select_by_value(obj, value):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_value(value)
    _add_step('Select \'{0}\' value in element {1}'.format(value, obj[2]))


def verify_text(text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    _add_step('Verify \'{0}\' is present in page'.format(text))
    if text not in driver.page_source:
        raise TextNotPresent(
                    "Text '{}' was not found in the page".format(text))


def verify_text_in_element(text, element):
    _run_wait_hook()
    print 'CORRI WAIT HOOK'
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    print 'Encontre el OBJETO'
    _add_step('Verify element \'{0}\' contains text \'{1}\''
                        .format(element[2], text))
    print 'TEXT', test_object.text
    if text not in test_object.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}"
                             .format(text, element[2]))


def verify_selected_option(element, text):
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    _add_step('Verify selected option of element \'{0}\' '
                        'is \'{1}\''
                        .format(element[2], text))
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(element[2], text))


def verify_is_not_enabled(element):
    #TODO
    _run_wait_hook()
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    _add_step('Verify the element \'{0}\' '
              'is not enabled'
              .format(element[2]))
    if test_object.is_enabled():
        raise Exception('Element is enabled')


def capture(msg=''):
    driver = core.getOrCreateWebdriver()
    #screenshot_name = 'test' + msg.replace(' ', '_')
    #screenshot_filename = .format(len(logger.screenshots))
    #driver.save_screenshot(screenshot_name + '.jpg')
    img = Image.open(StringIO.StringIO(driver.get_screenshot_as_png()))
    img_id = str(uuid.uuid4())[:8]
    logger.screenshots[img_id] = img
    _add_step(msg, img_id)


def close():
    driver = core.getOrCreateWebdriver()
    driver.quit()
    core.reset_driver_object()


def wait(seconds):
    try:
        to_int = int(seconds)
    except:
        raise Exception
    time.sleep(to_int)
