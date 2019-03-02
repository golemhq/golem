# from typing import List # not supported in 3.4
import time

from selenium.webdriver.remote.webelement import WebElement as RemoteWebElement
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select as SeleniumSelect
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from golem.webdriver.common import _find, _find_all
from golem.webdriver import golem_expected_conditions as gec


class ExtendedWebElement:

    selector_type = None
    selector_value = None
    name = None

    def check(self):
        """Check element if element is checkbox or radiobutton.
        If element is already checked, this is ignored.
        """
        checkbox_or_radio = (self.tag_name == 'input' and
                             self.get_attribute('type') in ['checkbox', 'radio'])
        if checkbox_or_radio:
            if not self.is_selected():
                self.click()
        else:
            msg = 'Element {} is not checkbox or radiobutton'.format(self.name)
            raise ValueError(msg)

    def double_click(self):
        """Double click the element"""
        action_chains = ActionChains(self.parent)
        action_chains.double_click(self).perform()

    def find(self, *args, **kwargs) -> 'ExtendedRemoteWebElement':
        """Find a WebElement

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        Other args:
        - timeout: timeout (in seconds) to wait for element to be present.
                   by default it uses the *search_timeout* setting value
        - wait_displayed: wait for element to be displayed (visible).
                          by default uses the *wait_displayed* setting value

        :Usage:
            element.find('div#someId > input.class')
            element.find(('id', 'someId'))
            element.find(id='someId')
            element.find(xpath='//div/input', timeout=5, wait_displayed=True)

        :Returns:
          a golem.webdriver.extended_webelement.ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return _find(self, **kwargs)

    #  -> List['ExtendedRemoteWebElement']
    def find_all(self, *args, **kwargs):
        """Find all WebElements that match the search criteria.

        Search criteria:
        The first argument must be: an element tuple, a CSS string or
        a WebElement object.
        Keyword search criteria: id, name, link_text, partial_link_text,
        css, xpath, tag_name.
        Only one search criteria should be provided.

        :Usage:
            element.find_all('div#someId > span.class')
            element.find(('tag_name', 'input'))
            element.find(xpath='//div/input')

        :Returns:
            a list of ExtendedRemoteWebElement
        """
        if len(args) == 1:
            kwargs['element'] = args[0]
        return _find_all(self, **kwargs)

    def focus(self):
        """Give focus to element"""
        self.parent.execute_script('arguments[0].focus();', self)

    def has_attribute(self, attribute):
        """Returns whether element has attribute"""
        return self.get_attribute(attribute) is not None

    def has_focus(self):
        """Returns whether element has focus"""
        script = 'return arguments[0] == document.activeElement'
        return self.parent.execute_script(script, self)

    @property
    def inner_html(self):
        """"Element innerHTML attribute"""
        return self.get_attribute('innerHTML')

    def javascript_click(self):
        """Click element using Javascript"""
        self.parent.execute_script('arguments[0].click();', self)

    def mouse_over(self):
        """Mouse over element"""
        action_chains = ActionChains(self.parent)
        action_chains.move_to_element(self).perform()

    @property
    def outer_html(self):
        """"Element outerHTML attribute"""
        return self.get_attribute('outerHTML')

    def press_key(self, key):
        """Press a key on element

        :Usage:
          element.press_key('ENTER')
          element.press_key('TAB')
          element.press_key('LEFT')
        """
        if hasattr(Keys, key):
            key_attr = getattr(Keys, key)
            self.send_keys(key_attr)
        else:
            defined_keys = [name for name in dir(Keys) if
                            not name.startswith('_')]
            error_msg = ('Key {} is invalid\n'
                         'valid keys are:\n'
                         '{}'.format(key, ','.join(defined_keys)))
            raise ValueError(error_msg)

    @property
    def select(self):
        """Return a Select object"""
        return Select(self)

    def send_keys_with_delay(self, value, delay=0.1):
        """Send keys to element one by one with a delay between keys.

        :Args:
         - value: a string to type
         - delay: time between keys (in seconds)

        :Raises:
         - ValueError: if delay is not a positive int or float
        """
        if not isinstance(delay, int) and not isinstance(delay, float):
            raise ValueError('delay must be int or float')
        elif delay < 0:
            raise ValueError('delay must be a positive number')
        else:
            for c in value:
                self.send_keys(c)
                time.sleep(delay)

    def uncheck(self):
        """Uncheck element if element is checkbox.
        If element is already unchecked, this is ignored.
        """
        is_checkbox = (self.tag_name == 'input' and
                       self.get_attribute('type') == 'checkbox')
        if is_checkbox:
            if self.is_selected():
                self.click()
        else:
            raise ValueError('Element {} is not checkbox'.format(self.name))

    @property
    def value(self):
        """The value attribute of element"""
        return self.get_attribute('value')

    def wait_displayed(self, timeout=30):
        """Wait for element to be displayed

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to be displayed'
                   .format(self.name))
        wait.until(ec.visibility_of(self), message=message)
        return self

    def wait_enabled(self, timeout=30):
        """Wait for element to be enabled

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = 'Timeout waiting for element {} to be enabled'.format(self.name)
        wait.until(gec.element_to_be_enabled(self), message=message)
        return self

    def wait_has_attribute(self, attribute, timeout=30):
        """Wait for element to have attribute

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to have attribute {}'
                   .format(self.name, attribute))
        wait.until(gec.element_to_have_attribute(self, attribute), message=message)
        return self

    def wait_has_not_attribute(self, attribute, timeout=30):
        """Wait for element to not have attribute

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to not have attribute {}'
                   .format(self.name, attribute))
        wait.until_not(gec.element_to_have_attribute(self, attribute),
                       message=message)
        return self

    def wait_not_displayed(self, timeout=30):
        """Wait for element to be not displayed

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} to be not displayed'
                   .format(self.name))
        wait.until_not(ec.visibility_of(self), message=message)
        return self

    def wait_not_enabled(self, timeout=30):
        """Wait for element to be not enabled

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = 'Timeout waiting for element {} to be not enabled'.format(self.name)
        wait.until_not(gec.element_to_be_enabled(self), message=message)
        return self

    def wait_text(self, text, timeout=30):
        """Wait for element text to match given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to be \'{}\''
                   .format(self.name, text))
        wait.until(gec.element_text_to_be(self, text), message=message)
        return self

    def wait_text_contains(self, text, timeout=30):
        """Wait for element to contain given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to contain \'{}\''
                   .format(self.name, text))
        wait.until(gec.element_text_to_contain(self, text), message=message)
        return self

    def wait_text_is_not(self, text, timeout=30):
        """Wait fo element text to not match given text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text not to be \'{}\''
                   .format(self.name, text))
        wait.until_not(gec.element_text_to_be(self, text), message=message)
        return self

    def wait_text_not_contains(self, text, timeout=30):
        """Wait for element text to not contain text

        :Returns:
          The element
        """
        wait = WebDriverWait(self.parent, timeout)
        message = ('Timeout waiting for element {} text to not contain \'{}\''
                   .format(self.name, text))
        wait.until_not(gec.element_text_to_contain(self, text),
                       message=message)
        return self


class Select(SeleniumSelect):

    @property
    def first_selected_option(self):
        """Return the first selected option as a
        Golem ExtendedWebElement"""
        option = super(Select, self).first_selected_option
        return extend_webelement(option)


class ExtendedRemoteWebElement(RemoteWebElement, ExtendedWebElement):
    pass


class ExtendedFirefoxWebElement(FirefoxWebElement, ExtendedWebElement):
    pass


def extend_webelement(web_element) -> ExtendedRemoteWebElement:
    """Extend the selenium WebElement using the
    ExtendedRemoteWebElement or ExtendedFirefoxWebElement class
    """
    if isinstance(web_element.parent, FirefoxDriver):
        web_element.__class__ = ExtendedFirefoxWebElement
    else:
        web_element.__class__ = ExtendedRemoteWebElement
    return web_element

