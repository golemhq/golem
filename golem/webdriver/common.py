import time

from selenium.webdriver.remote.webelement import WebElement

from golem import execution
from golem.core.exceptions import IncorrectSelectorType, ElementNotFound
from .extended_webelement import extend_webelement, ExtendedWebElement


def _find_webelement(root, selector_type, selector_value,
                     element_name, remaining_time):
    """Finds a web element."""
    webelement = None
    start_time = time.time()
    try:
        if selector_type == 'id':
            webelement = root.find_element_by_id(selector_value)
        elif selector_type == 'css':
            webelement = root.find_element_by_css_selector(selector_value)
        elif selector_type == 'text':
            webelement = root.find_element_by_css_selector("text[{}]".format(selector_value))
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
            msg = 'Selector {0} is not a valid option'.format(selector_type)
            raise IncorrectSelectorType(msg)
        execution.logger.debug('Element found')
    except:
        time.sleep(0.5)
        end_time = time.time()
        remaining_time -= end_time - start_time
        if remaining_time > 0:
            execution.logger.debug('Element not found yet, remaining time: {}'.format(remaining_time))
            webelement = _find_webelement(root, selector_type, selector_value,
                                          element_name, remaining_time)
        else:
            raise ElementNotFound('Element {0} not found using selector {1}:\'{2}\''
                                  .format(element_name, selector_type, selector_value))
    
    # Use remaining time to wait until element is visible (is_displayed)
    # TODO add this as a setting
    remaining_time = remaining_time - (time.time() - start_time)
    while not webelement.is_displayed() and remaining_time > 0:
        # Element is not visible yet
        execution.logger.debug('Element still not visible, waiting')
        time.sleep(0.5)
        remaining_time = remaining_time - (time.time() - start_time)

    if not webelement.is_displayed():
        execution.logger.debug('Element not visible, continuing..')

    return webelement


def _find(self, element=None, id=None, name=None, text=None,
          link_text=None, partial_link_text=None, css=None,
          xpath=None, tag_name=None, timeout=None):
    """Find a webelement.

    `element` can be:
      a web element
      a tuple with the format (<selector_type>, <selector_value>, [<display_nane>])
      a css selector string
    """
    webelement = None

    selector_type = None
    selector_value = None
    element_name = None

    if timeout is None:
        timeout = execution.settings['implicit_wait']

    if isinstance(element, WebElement) or isinstance(element, ExtendedWebElement):
        webelement = element
    elif isinstance(element, tuple):
        selector_type = element[0]
        selector_value = element[1]
        element_name = element[2] if len(element) == 3 else element[1]
    elif isinstance(element, str):
        selector_type = 'css'
        selector_value = element
        element_name = element
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
    
    if not webelement:
        webelement = _find_webelement(self, selector_type, selector_value,
                                      element_name, timeout)
        webelement.selector_type = selector_type
        webelement.selector_value = selector_value
        webelement.name = element_name

    return extend_webelement(webelement)


def _find_all(self, element=None, id=None, name=None, text=None, link_text=None,
              partial_link_text=None, css=None, xpath=None, tag_name=None):
    """Find all webelements

    `element` can be:
      a web element
      a tuple with the format (<selector_type>, <selector_value>, [<display_nane>])
      a css selector string
    """
    webelements = []
    tuple_element_name = None
    if isinstance(element, tuple):
        selector_type = element[0]
        selector_value = element[1]
        tuple_element_name = element[2] if len(element) >= 3 else element[1]
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
        else:
            raise Exception('Incorrect element {}'.format(element))
    elif isinstance(element, str):
        css = element

    if id:
        selector_type = 'id'
        selector_value = id
        element_name = tuple_element_name or id
        webelements = self.find_elements_by_id(id)
    elif css:
        selector_type = 'css'
        selector_value = css
        element_name = tuple_element_name or css
        webelements = self.find_elements_by_css_selector(css)
    elif text:
        selector_type = 'text'
        selector_value = text
        element_name = tuple_element_name or text
        webelements = self.find_elements_by_css_selector("text[{}]".format(text))
    elif link_text:
        selector_type = 'link_text'
        selector_value = link_text
        element_name = tuple_element_name or link_text
        webelements = self.find_elements_by_link_text(link_text)
    elif partial_link_text:
        selector_type = 'partial_link_text'
        selector_value = partial_link_text
        element_name = tuple_element_name or partial_link_text
        webelements = self.find_elements_by_partial_link_text(partial_link_text)
    elif name:
        selector_type = 'name'
        selector_value = name
        element_name = tuple_element_name or name
        webelements = self.find_elements_by_name(name)
    elif xpath:
        selector_type = 'xpath'
        selector_value = xpath
        element_name = tuple_element_name or xpath
        webelements = self.find_elements_by_xpath(xpath)
    elif tag_name:
        selector_type = 'tag_name'
        selector_value = element_name = tag_name
        element_name = tuple_element_name or tag_name
        webelements = self.find_elements_by_tag_name(tag_name)
    else:
        raise IncorrectSelectorType('Incorrect selector provided')

    extended_webelements = []
    for elem in webelements:
        elem.selector_type = selector_type
        elem.selector_value = selector_value
        elem.name = element_name
        extended_webelements.append(extend_webelement(elem))

    return extended_webelements
