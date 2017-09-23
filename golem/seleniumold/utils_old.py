import time
import types

import selenium
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from golem import core
from golem.core import data
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound


def _find_selenium_object(selector_type, selector_value, element_name, driver, remaining_time):
    test_object = None
    start_time = time.time()
    try:
        if selector_type == 'id':
            test_object = driver.find_element_by_id(selector_value)
        elif selector_type == 'css':
            test_object = driver.find_element_by_css_selector(selector_value)
        elif selector_type == 'text':
            test_object = driver.find_element_by_css_selector(
                                    "text[{}]".format(selector_value))
        elif selector_type == 'link_text':
            test_object = driver.find_element_by_link_text(selector_value)
        elif selector_type == 'partial_link_text':
            test_object = driver.find_element_by_partial_link_text(selector_value)
        elif selector_type == 'name':
            test_object = driver.find_element_by_name(selector_value)
        elif selector_type == 'xpath':
            test_object = driver.find_element_by_xpath(selector_value)
        elif selector_type == 'tag_name':
            test_object = driver.find_element_by_tag_name(selector_value)
        else:
            raise IncorrectSelectorType(
                    'Selector {0} is not a valid option'.format(selector_type))
    except:
        time.sleep(0.5)
        end_time = time.time()
        new_remaining_time = remaining_time - (end_time - start_time)
        if new_remaining_time > 0:
            test_object = _find_selenium_object(selector_type, selector_value, element_name, 
                                                driver, new_remaining_time)
        else:
            raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
                                  .format(element_name, selector_type, selector_value))
    return test_object


def get_selenium_object(elem, driver=None, implicit_wait=None):
    is_webelement_descendant = (
            selenium.webdriver.remote.webelement.WebElement in elem.__class__.__bases__)
    is_webelement = type(elem) == selenium.webdriver.remote.webelement.WebElement
    if is_webelement or is_webelement_descendant:
        return elem
    elif type(elem) == tuple:
        if not driver:
            driver = core.get_or_create_webdriver()
        test_object = None
        if implicit_wait is None:
            implicit_wait = core.get_setting('implicit_wait')
        selector_type = elem[0]
        selector_value = elem[1]
        # if there is no 'element name' use the selector value instead
        element_name = selector_value
        if len(elem) == 3:
            element_name = elem[2]
        test_object = _find_selenium_object(selector_type, selector_value, element_name,
                                            driver, implicit_wait)
        test_object.selector_type = selector_type
        test_object.selector_value = selector_value
        test_object.name = element_name
        return test_object
    else:
        raise Exception('Invalid element to get')


def get_selenium_objects(elem, driver=None):
    if not driver:
        driver = core.get_or_create_webdriver()
    selector_type = elem[0]
    selector_value = elem[1]
    test_objects = []
    if selector_type == 'id':
        test_objects = driver.find_elements_by_id(selector_value)
    elif selector_type == 'css':
        print('SELECTOR', selector_value)
        test_objects = driver.find_elements_by_css_selector(selector_value)
    elif selector_type == 'text':
        test_objects = driver.find_elements_by_css_selector(
                                    "text[{}]".format(selector_value))
    elif selector_type == 'link_text':
        test_objects = driver.find_elements_by_link_text(selector_value)
    elif selector_type == 'partial_link_text':
        test_objects = driver.find_elements_by_partial_link_text(selector_value)
    elif selector_type == 'name':
        test_objects = driver.find_elements_by_name(selector_value)
    elif selector_type == 'xpath':
        test_objects = driver.find_elements_by_xpath(selector_value)
    elif selector_type == 'tag_name':
        test_objects = driver.find_elements_by_tag_name(selector_value)
    else:
        raise IncorrectSelectorType(
            'Selector {0} is not a valid option'.format(selector_type))
    return test_objects


def _find(self, element_tuple=None, id=None, name=None, text=None, link_text=None,
          partial_link_text=None, css=None, xpath=None, tag_name=None):
    print('SELF', self)
    return element(self, element_tuple, id, name, text, link_text, partial_link_text, css,
                   xpath, tag_name)


def _find_all(self, element_tuple=None, id=None, name=None, text=None, link_text=None,
              partial_link_text=None, css=None, xpath=None, tag_name=None):
    return elements(element_tuple, id, name, text, link_text, partial_link_text, css,
                    xpath, tag_name)


def element(element, element_tuple=None, id=None, name=None, text=None, link_text=None,
            partial_link_text=None, css=None, xpath=None, tag_name=None):
    webelement = None
    selector = None
    if type(element_tuple) == tuple:
        webelement = get_selenium_object(element_tuple)
    elif id:
        webelement = get_selenium_object(('id', id, 'element_name'))
    elif name:
        webelement = get_selenium_object(('name', name, 'element_name'))
    elif text:
        webelement = get_selenium_object(('text', text, 'element_name'))
    elif link_text:
        webelement = get_selenium_object(('link_text', link_text, 'element_name'))
    elif partial_link_text:
        webelement = get_selenium_object(('partial_link_text', partial_link_text,
                                          'element_name'))
    elif css:
        webelement = get_selenium_object(('css', css, 'element_name'))
    elif xpath:
        webelement = get_selenium_object(('xpath', xpath, 'element_name'))
    elif tag_name:
        webelement = get_selenium_object(('tag_name', tag_name, 'element_name'))
    else:
         raise IncorrectSelectorType('Selector is not a valid option')
    # bound find and find_all functions to the WebElement instance
    webelement.find = types.MethodType(_find, webelement)
    webelement.find_all = types.MethodType(_find_all, webelement)
    return webelement


def elements(element_tuple=None, id=None, name=None, text=None, link_text=None,
             partial_link_text=None, css=None, xpath=None, tag_name=None):
    webelements = None
    if type(element_tuple) == tuple:
        webelements = get_selenium_objects(element_tuple)
    elif id:
        webelements = get_selenium_objects(('id', id, 'element_name'))
    elif name:
        webelements = get_selenium_objects(('name', name, 'element_name'))
    elif text:
        webelements = get_selenium_objects(('text', text, 'element_name'))
    elif link_text:
        webelements = get_selenium_objects(('link_text', link_text, 'element_name'))
    elif partial_link_text:
        webelements = get_selenium_objects(('partial_link_text', partial_link_text,
                                            'element_name'))
    elif css:
        webelements = get_selenium_objects(('css', css, 'element_name'))
    elif xpath:
        webelements = get_selenium_objects(('xpath', xpath, 'element_name'))
    elif tag_name:
        webelements = get_selenium_objects(('tag_name', tag_name, 'element_name'))
    else:
         raise IncorrectSelectorType('Selector is not a valid option')
    # bound find and find_all functions to each WebElement instance
    for webelement in webelements:
        webelement.find = types.MethodType(_find, webelement)
        webelement.find_all = types.MethodType(_find_all, webelement)
    return webelements
