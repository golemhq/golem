import time

import selenium

from golem import core
from golem.core import execution_logger as logger
from golem.core.exceptions import TextNotPresent
from golem.core.selenium_utils import get_selenium_object


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


def close():
    driver = core.getOrCreateWebdriver()
    driver.quit()
