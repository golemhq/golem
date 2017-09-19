import time
import types

import selenium
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from golem import core
from golem.core import data
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound


def _find_selenium_element(root, selector_type, selector_value, element_name, remaining_time):
    webelement = None
    start_time = time.time()
    try:
        if selector_type == 'id':
            webelement = root.find_element_by_id(selector_value)
        elif selector_type == 'css':
            webelement = root.find_element_by_css_selector(selector_value)
        elif selector_type == 'text':
            webelement = root.find_element_by_css_selector(
                                    "text[{}]".format(selector_value))
        elif selector_type == 'link_text':
            webelement = root.find_element_by_link_text(selector_value)
        elif selector_type == 'partial_link_text':
            webelement = root.find_element_by_partial_link_text(selector_value)
        elif selector_type == 'name':
            webelement = root.find_element_by_name(selector_value)
        elif selector_type == 'xpath':
            webelement = root.find_element_by_xpath(selector_value)
        elif selector_type == 'tag_name':
            webelement = root.find_element_by_tag_name(selector_value)
        else:
            raise IncorrectSelectorType(
                    'Selector {0} is not a valid option'.format(selector_type))
    except:
        time.sleep(0.5)
        end_time = time.time()
        new_remaining_time = remaining_time - (end_time - start_time)
        if new_remaining_time > 0:
            webelement = _find_selenium_element(root, selector_type, selector_value,
                                                element_name, new_remaining_time)
        else:
            raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
                                  .format(element_name, selector_type, selector_value))
    return webelement


# def get_selenium_objects(elem, driver=None):
#     if not driver:
#         driver = core.get_or_create_webdriver()
#     selector_type = elem[0]
#     selector_value = elem[1]
#     test_objects = []
#     if selector_type == 'id':
#         test_objects = driver.find_elements_by_id(selector_value)
#     elif selector_type == 'css':
#         print('SELECTOR', selector_value)
#         test_objects = driver.find_elements_by_css_selector(selector_value)
#     elif selector_type == 'text':
#         test_objects = driver.find_elements_by_css_selector(
#                                     "text[{}]".format(selector_value))
#     elif selector_type == 'link_text':
#         test_objects = driver.find_elements_by_link_text(selector_value)
#     elif selector_type == 'partial_link_text':
#         test_objects = driver.find_elements_by_partial_link_text(selector_value)
#     elif selector_type == 'name':
#         test_objects = driver.find_elements_by_name(selector_value)
#     elif selector_type == 'xpath':
#         test_objects = driver.find_elements_by_xpath(selector_value)
#     elif selector_type == 'tag_name':
#         test_objects = driver.find_elements_by_tag_name(selector_value)
#     else:
#         raise IncorrectSelectorType(
#             'Selector {0} is not a valid option'.format(selector_type))
#     return test_objects


def _find(self, element_tuple=None, id=None, name=None, text=None, link_text=None,
          partial_link_text=None, css=None, xpath=None, tag_name=None, timeout=0):
    webelement = None

    selector_type = None
    selector_value = None
    element_name = None

    if type(element_tuple) == tuple:
        selector_type = element_tuple[0]
        selector_value = element_tuple[1]
        element_name = element_tuple[2] if len(element_tuple) == 3 else element_tuple[1]
    elif id:
        selector_type = 'id'
        selector_value = element_name = id
    elif name:
        selector_type = 'name'
        selector_value = element_name = name
    elif text:
        selector_type = 'text'
        selector_value = element_name = text
    elif link_text:
        selector_type = 'link_text'
        selector_value = element_name = link_text
    elif partial_link_text:
        selector_type = 'partial_link_text'
        selector_value = element_name = partial_link_text
    elif css:
        selector_type = 'css'
        selector_value = element_name = css
    elif xpath:
        selector_type = 'xpath'
        selector_value = element_name = xpath
    elif tag_name:
        selector_type = 'tag_name'
        selector_value = element_name = tag_name
    else:
         raise IncorrectSelectorType('Selector is not a valid option')
    webelement = _find_selenium_element(self, selector_type, selector_value,
                                        element_name, timeout)
    webelement.selector_type = selector_type
    webelement.selector_value = selector_value
    webelement.name = element_name
    webelement.find = types.MethodType(_find, webelement)
    webelement.find_all = types.MethodType(_find_all, webelement)

    return webelement


def _find_all(self, element_tuple=None, id=None, name=None, text=None, link_text=None,
              partial_link_text=None, css=None, xpath=None, tag_name=None, timeout=0):
    webelements = []
    selector_type = None
    selector_value = None
    element_name = None
    if type(element_tuple) == tuple:
        selector_type = element_tuple[0]
        selector_value = element_name = element_tuple[1]
        if selector_type == 'id':
            id = selector_value
        elif selector_type == 'css':
            css = selector_value
        elif selector_type == 'text':
            text = selector_value
        elif selector_type == 'link_text':
            link_text = selector_value
        elif selector_type == 'partial_link_text':
            partial_link_text = selector_value
        elif selector_type == 'name':
            name = selector_value
        elif selector_type == 'xpath':
            xpath = selector_value
        elif selector_type == 'tag_name':
            tag_name = selector_value
    if id:
        selector_type = 'id'
        selector_value = element_name = id
        webelements = self.find_elements_by_id(id)
    elif css:
        selector_type = 'css'
        selector_value = element_name = css
        webelements = self.find_elements_by_css_selector(css)
    elif text:
        selector_type = 'text'
        selector_value = element_name = text
        webelements = self.find_elements_by_css_selector(
                                    "text[{}]".format(text))
    elif link_text:
        selector_type = 'link_text'
        selector_value = element_name = link_text
        webelements = self.find_elements_by_link_text(link_text)
    elif partial_link_text:
        selector_type = 'partial_link_text'
        selector_value = element_name = partial_link_text
        webelements = self.find_elements_by_partial_link_text(partial_link_text)
    elif name:
        selector_type = 'name'
        selector_value = element_name = name
        webelements = self.find_elements_by_name(name)
    elif xpath:
        selector_type = 'xpath'
        selector_value = element_name = xpath
        webelements = self.find_elements_by_xpath(xpath)
    elif tag_name:
        selector_type = 'tag_name'
        selector_value = element_name = tag_name
        webelements = self.find_elements_by_tag_name(tag_name)
    else:
        raise IncorrectSelectorType('Incorrect selector provided')

    for elem in webelements:
        elem.selector_type = selector_type
        elem.selector_value = selector_value
        elem.name = element_name
        elem.find = types.MethodType(_find, elem)
        elem.find_all = types.MethodType(_find_all, elem)

    return webelements


def element(*args, **kwargs):
    if len(args) == 1:
        kwargs['element_tuple'] = args[0]
    webelement = core.get_or_create_webdriver().find(**kwargs)
    return webelement


def get_driver():
    return core.get_or_create_webdriver()

# def elements(element_tuple=None, id=None, name=None, text=None, link_text=None,
#              partial_link_text=None, css=None, xpath=None, tag_name=None):
#     webelements = None
#     if type(element_tuple) == tuple:
#         webelements = get_selenium_objects(element_tuple)
#     elif id:
#         webelements = get_selenium_objects(('id', id, 'element_name'))
#     elif name:
#         webelements = get_selenium_objects(('name', name, 'element_name'))
#     elif text:
#         webelements = get_selenium_objects(('text', text, 'element_name'))
#     elif link_text:
#         webelements = get_selenium_objects(('link_text', link_text, 'element_name'))
#     elif partial_link_text:
#         webelements = get_selenium_objects(('partial_link_text', partial_link_text,
#                                             'element_name'))
#     elif css:
#         webelements = get_selenium_objects(('css', css, 'element_name'))
#     elif xpath:
#         webelements = get_selenium_objects(('xpath', xpath, 'element_name'))
#     elif tag_name:
#         webelements = get_selenium_objects(('tag_name', tag_name, 'element_name'))
#     else:
#          raise IncorrectSelectorType('Selector is not a valid option')
#     # bound find and find_all functions to each WebElement instance
#     for webelement in webelements:
#         webelement.find = types.MethodType(_find, webelement)
#         webelement.find_all = types.MethodType(_find_all, webelement)
#     return webelements
