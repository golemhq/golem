# -*- coding: utf-8 -*-
import time
import uuid
import StringIO

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


def click(obj):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    test_object.click()
    logger.steps.append('Click {0}'.format(obj[2]))


def go_to(url):
    driver = core.getOrCreateWebdriver()
    driver.get(url)
    logger.steps.append('Go to url:\'{0}\''.format(url))


def send_keys(obj, text):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    test_object.send_keys(text)
    logger.steps.append('Write \'{0}\' in element {1}'.format(text, obj[2]))


def select_by_text(obj, text):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_visible_text(text)
    logger.steps.append('Select \'{0}\' from element {1}'.format(text, obj[2]))


def select_by_index(obj, index):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_index(index)
    logger.steps.append('Select index \'{0}\' in element {1}'.format(index, obj[2]))


def select_by_value(obj, value):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(obj, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    select.select_by_value(value)
    logger.steps.append('Select \'{0}\' value in element {1}'.format(value, obj[2]))


def verify_text(text):
    driver = core.getOrCreateWebdriver()
    logger.steps.append('Verify \'{0}\' is present in page'.format(text))
    if text not in driver.page_source:
        raise TextNotPresent(
                    "Text '{}' was not found in the page".format(text))


def verify_text_in_element(text, element):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    logger.steps.append('Verify element \'{0}\' contains text \'{1}\''
                        .format(element[2], text))
    if text not in test_object.text:
        raise TextNotPresent("Text \'{0}\' was not found in element {1}"
                             .format(text, element[2]))


def verify_selected_option(element, text):
    driver = core.getOrCreateWebdriver()
    test_object = get_selenium_object(element, driver)
    select = selenium.webdriver.support.select.Select(test_object)
    logger.steps.append('Verify selected option of element \'{0}\' '
                        'is \'{1}\''
                        .format(element[2], text))
    print 'OPTION', select.first_selected_option.text
    if not select.first_selected_option.text == text:
        raise TextNotPresent('Option selected in element \'{0}\' '
                             'is not {1}'
                             .format(element[2], text))


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
